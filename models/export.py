# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.addons.test_convert.tests.test_env import record
from odoo.exceptions import ValidationError
import logging
# import pypandoc
import datetime
import pytz

import jdatetime
from jdatetimext import j_start, j_start_end_js, jdatejs
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.shared import Pt
from io import BytesIO
import base64
import os
from tempfile import NamedTemporaryFile
from odoo.tools import html_escape
from bs4 import BeautifulSoup
from icecream import ic
import zipfile
import io
import subprocess
import uuid
import tempfile

J_DATE_FORMAT = "%Y/%m/%d"
B_NAZANIN = 'B Nazanin'
B_YEKAN = 'B Yekan'
IRANSansFaNum = 'IRANSansFaNum'
ARIAL = 'Arial'


class SdHrExport(models.Model):
    _name = 'sd_hr.export'
    _description = 'sd_hr.export'

    def generate_and_download(self, model_name=None, res_ids=None, variable_no=None, output_type='pdf', file_prefix='DL', file_name=['name'], attach_docs=False ):
        # logging.info(f"\n >>>> generate_and_download:\n model_name:{model_name}\nres_ids: {res_ids}\nvariable_no: {variable_no}")
        output_ext = '.pdf'
        if model_name and len(res_ids) > 0:
            records = self.env[model_name].sudo().browse(res_ids)
            if len(records) > 1 or attach_docs:
                if output_type == 'docx':
                    output_type = 'zip_docx'
                    output_ext = '.docx'
                else:
                    output_type = 'zip_pdf'
                    output_ext = '.pdf'
            elif output_type == 'docx':
                output_ext = '.docx'
            else:
                output_ext = '.pdf'
        else:
            records = []

        # if self.env.context.get('active_model', False) == 'hr.contract':
        #     records = self.browse(self.env.context.get('active_ids', False))
        # else:
        #     records = []

        # logging.info(f"\n records:\n {self.env.context}\n {records} {self}")
        attachment_model = self.env['ir.attachment']
        hr_documents = self.env['sd_hr_documents.attachments']
        if len(records) > 1 or attach_docs:
            zip_buffer = io.BytesIO()
            today = datetime.datetime.now(pytz.timezone(self.env.context.get('tz', 'GMT')))

            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for rec in records:
                    if rec.employee_id:
                        employee_name = (rec.employee_id.with_context(lang='en_US').name_cv).replace('/', '_')
                        employee_title = (rec.employee_id.with_context(lang='en_US').job_title).replace('/', '_') if rec.employee_id.job_title else 'Title'
                        zip_dir_name = f"[{employee_name}]_[{employee_title}]"
                    else:
                        zip_dir_name = 'Other'

                    zip_folder = zip_dir_name if attach_docs else f"IPAC_Resume_{jdatejs(today, '%Y%m%d')}_{today.strftime('%H%M%S')}"
                    doc_content = self.regenerate_template(rec, variable_no, output_type)
                    zip_file.writestr(f"{zip_folder}/{self.file_name_generator(rec, file_prefix, file_name, output_ext)}", doc_content)
                    # TODO: if name contains "/", it creates a folder based of str befor it
                    if attach_docs:
                        documents = hr_documents.search([('employee_id', '=', rec.employee_id.id), ('resume_document', '=', True)])
                        for document in documents:
                            for att in document.attachments:
                                zip_file.writestr(f"{zip_folder}/{att.name}", base64.b64decode(att.datas))

            zip_buffer.seek(0)
            zip_buffer = base64.b64encode(zip_buffer.getvalue()).decode('utf-8')

            # zip_buffer
            # logging.info(zip_buffer)
            attach_id = attachment_model.create({
                'res_model': self._name,
                'res_field': 'output_file',
                'res_id': self.id,
                'datas': zip_buffer,
                'name': f"Contracts_{jdatejs(today, '%Y%m%d')}_{today.strftime('%H%M%S')}",
                'type': 'binary',
            })
            download_url = '/web/content/%s' % attach_id.id
            # logging.info(f"\n >>>>>>>> download_url ZIP: {download_url}")

            return { 'type': 'ir.actions.act_url',
                     'url': download_url,
                     'target': 'self',
                     }
        else:
            record = records if len(records) == 1 else self
            doc_content = self.regenerate_template(record, variable_no, output_type)  # Your function to create `.docx` content

            attach_id = attachment_model.search([('res_model', '=', self._name),
                                                 ('res_id', '=', record.id),
                                                 ('res_field', '=', 'output_file'),
                                                 ])
            # logging.warning(f">>>>>>>>>  attach_id {attach_id}")
            # return
            if  len(attach_id) > 1:
                for att in attach_id:
                    att.unlink()
                attach_id = False

            if attach_id:
                attach_id.write({
                    'datas': doc_content,
                    'name': self.file_name_generator(record, file_prefix, file_name, output_ext),

                })
                # logging.warning(f">>>>>>>>> is attach_id")
            else:
                # logging.warning(f">>>>>>>>> is NOT attach_id")
                attach_id = attachment_model.create({
                    'res_model': record._name,
                    'res_field': doc_content,
                    'res_id': record.id,
                    'datas': doc_content,
                    # 'name': 'aaaaa.docx',
                    'name': self.file_name_generator(record, file_prefix, file_name, output_ext),
                    'type': 'binary',
                })
            # Note: If not download=1, it opens the pdf file instead of download.
            download_url = '/web/content/%s?download=1' % attach_id.id
            # download_url = '/web/content/%s' % attach_id.id
            # logging.info(f"\n >>>>>>>> download_url DOCX: {download_url}")
            return { 'type': 'ir.actions.act_url',
                     'url': download_url,
                     'target': 'self',
                     }

    def file_name_generator(self, rec, file_prefix='File', file_name='name', output_ext='.pdf'):
        file_name_list = list([f"[{rec[r]}]" for r in file_name if r in rec._fields])
        return f"{file_prefix}_{'_'.join(file_name_list)}{output_ext}"

    def regenerate_template(self, record, variable_no=None, output_type='pdf'):

        '''
        Get variables from 'sd_hr.variables' then replaces new_values on the docx document.

        :return:
        '''
        # records = self.env[model_name].browse(res_ids)
        # logging.info(f">>>> regenerate_template \n record:{record} \n variable_no:{variable_no}")
        if variable_no:
            doc_template = self.env['sd_hr.doc_template'].search([('variable_no', '=', variable_no)])
            if doc_template and doc_template.template_file:
                template_file = doc_template.template_file
            else:
                raise ValidationError(f'There is no template file for variable_no:{variable_no}')


        elif record._fields.get('doc_template', False) and record.doc_template:
            doc_template_id = record.doc_template
            template_file = record.doc_template.template_file
        else:
            # record.output_file = ''
            raise ValidationError('There is no template file')
        
            
        variables = []
        value_function_list = []
        numeral_variables = []
        html_variables = []
        variables_dict = {}
        html_content = ''
        # TODO: to make it general we need to make document template module as a general module.

        # hr_contract_model = self.env['ir.model'].sudo().search([('model', '=', 'hr.contract')])
        # if hr_contract_model:
        if True:
            variables = self.env['sd_hr.variables'].sudo().search([('variable_no', '=', variable_no),])
            # logging.info(f"\n>>>>>>>>>>>>>>>variables:{variables}")
            if variables:
                variables_dict = dict({rec.variable: (rec.value_text, self.get_select(rec, 'value_fonts')) if rec.value_source == 'text' else (rec.value_function, self.get_select(rec, 'value_fonts')) for rec in variables})
                value_function_list = list([rec.variable for rec in variables if rec.value_source == 'function'])

        # Load the .docx file from the binary field

        template_file_b = base64.b64decode(template_file)
        template = Document(BytesIO(template_file_b))

        for paragraph in template.paragraphs:
            for run in paragraph.runs:
                for variable, new_value in variables_dict.items():
                    if variable in run.text:
                        self.replace_run(record, paragraph, run, variable, value_function_list, numeral_variables,
                                    html_variables, new_value[0], new_value[1] )

        for table in template.tables:
            for row in table.rows:
                for cell in row.cells:
                    runs = cell.paragraphs[0].runs
                    for run in runs:
                        for variable, new_value in variables_dict.items():
                            if variable in run.text:
                                self.replace_run(record, table, run, variable, value_function_list, numeral_variables,
                                                 html_variables, new_value[0], new_value[1])

        for doc_sections in template.sections:
            doc_sections_list = [doc_sections.header,
                                 doc_sections.footer,
                                 doc_sections.first_page_header,
                                 doc_sections.first_page_footer,
                                 ]
            for doc_section in doc_sections_list:
                for paragraph in doc_section.paragraphs:
                    for run in paragraph.runs:
                        for variable, new_value in variables_dict.items():
                            if variable in run.text:
                                self.replace_run(record, paragraph, run, variable, value_function_list, numeral_variables,
                                                 html_variables, new_value[0], new_value[1])

                for table in doc_section.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            runs = cell.paragraphs[0].runs
                            for run in runs:
                                for variable, new_value in variables_dict.items():
                                    if variable in run.text:
                                        self.replace_run(record, table, run, variable, value_function_list,
                                                         numeral_variables,
                                                         html_variables, new_value[0], new_value[1])


        # Save the modified file into a binary field
        output_stream = BytesIO()
        template.save(output_stream)
        docx_output_file = base64.b64encode(output_stream.getvalue())
        output_file = ''
        if output_type in ['pdf', 'zip_pdf']:
            try:
                temp_dir = os.path.join(tempfile.gettempdir(), "my_odoo_temp")
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir, mode=0o777)

                filename = str(uuid.uuid4())
                filename_pdf = os.path.join(temp_dir, filename + '.pdf')
                filename_docx = os.path.join(temp_dir, filename + '.docx')

                logging.info(f"\n ongoing:  {filename_docx} --> {filename_pdf}")
                with open(filename_docx, "wb") as f:
                    f.write(output_stream.getvalue())
                logging.info(f"\n created:  {filename_docx}")

                self.convert_docx_to_pdf(filename_docx, temp_dir)
                logging.info(f"\n created:  {filename_docx}")

                with open(filename_pdf, "rb") as f:
                    pdf_data_b = f.read()
                    pdf_data =  base64.b64encode(pdf_data_b)
                    os.remove(filename_pdf)
                    os.remove(filename_docx)
                output_file = pdf_data_b if output_type == 'zip_pdf' else pdf_data
            except Exception as e:
                logging.error(f"[ERROR] {e}")
        elif output_type == 'docx':
            output_file = docx_output_file
        elif output_type == 'zip_docx':
            # output_stream.getvalue()
            # docx_output_file.seek(0)
            output_file = output_stream.getvalue()


        output_stream.close()
        return output_file

    def generate_and_download_docx_old(self):
        self.regenerate_template()

#         download_url = f'/web/hrcontracts/download/?id={self.id}'
#         logging.info(f"""
#         self._name: {self._name}
#         self._origin.id: {self._origin.id}
#     download_url: {download_url}
# """)
        attachment_model = self.env['ir.attachment']
        attach_id = attachment_model.search([('res_model', '=', self._name),
                                             ('res_id', '=', self.id),
                                             ('res_field', '=', 'output_file'),
                                             ])
        # logging.warning(f">>>>>>>>>  attach_id {attach_id}")
        if  len(attach_id) > 1:
            for rec in attach_id:
                rec.unlink()
            attach_id = False

        if attach_id:
            attach_id.write({
                'datas': self.output_file,
                'name': self.output_file_name,

            })
            # logging.warning(f">>>>>>>>> is attach_id")
        else:
            # logging.warning(f">>>>>>>>> is NOT attach_id")
            attach_id = attachment_model.create({
                'res_model': self._name,
                'res_field': 'output_file',
                'res_id': self.id,
                'datas': self.output_file,
                'name': self.output_file_name,
                'type': 'binary',
            })

        download_url = '/web/content/%s' % attach_id.id
        return { 'type': 'ir.actions.act_url',
                 'url': download_url,
                 'target': 'self',
                 }

    def set_english_font(self, run, font_name=B_NAZANIN):
        run.font.name =  font_name
        # Set an appropriate English
        # run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
        run.font.size = Pt(12) # Set font size as needed

    def replace_run(self, record, paragraph, run, variable, value_function_list, numeral_variables, html_variables, new_value, font_name=B_NAZANIN):
        try:
            if variable in value_function_list:
                run.text = run.text.replace(variable, str(eval(new_value) or ''))
            else:
                run.text = run.text.replace(variable, str(new_value) or '')

            if variable in numeral_variables:
                self.set_english_font(run, font_name)
            elif variable in html_variables:
                self.add_html_to_paragraph(paragraph, str(eval(new_value)  or ''), font_name)
            else:
                run.font.name = font_name
        except Exception as e:
            logging.error(f"replace_run > {variable} > {e} ")

    def add_html_to_paragraph(self, paragraph, html, font_name=B_NAZANIN):
        soup = BeautifulSoup(html, 'html.parser')

        for element in soup:
            if element.name == 'strong':
                run = paragraph.add_run(element.get_text())
                run.bold = True
                run.font.name = font_name

            elif element.name == 'li':
                run = paragraph.add_run(f"• {element.get_text()}\n")
                run.font.name = font_name

            elif element.name is None:
                run = paragraph.add_run(element)
                run.font.name = font_name

    def fix_persian(self, date_text):
        """
        Replaces standard slashes with Persian slashes.
        :param date_text: The input date string (e.g., '1403/10/01').
        :return: The date string with Persian slashes.
        """
        return date_text
        return date_text.replace("/", ",").replace("-", "\u659C")

    def fix_persian_ordering(self, text):
        """
        Fixes Persian numbering and text ordering issues by applying RTL control characters.
        :param text: The input text (e.g., '1403/10/01').
        :return: The fixed text for proper display.
        """
        rtl_override = "\u202E"
        pop_directional = "\u202C"
        # return f"{rtl_override}{text}{pop_directional}"
        return f"{text}{pop_directional}"

    def replace_table_placeholders(self, document, replacements, font_name=B_NAZANIN):
        """
        Replaces placeholders in tables within a Word document.
        :param document: Document object
        :param replacements: Dictionary with placeholder keys and their values
        """
        for table in document.tables:
            # table.font.name = B_NAZANIN
            for row in table.rows:
                for cell in row.cells:
                    runs = cell.paragraphs[0].runs
                    for run in runs:
                        for placeholder, value in replacements.items():
                            if placeholder in run.text:
                                run.text = run.text.replace(placeholder, value)
                                run.font.name = font_name

    def _replace_and_format(self, paragraph, placeholder, value, bold=False, font_name=B_NAZANIN, italic=False, font_size=None, color=None):
        """
        Replace a placeholder with formatted text in a paragraph.
        """
        if placeholder in paragraph.text:
            # Split the paragraph text and preserve formatting
            parts = paragraph.text.split(placeholder)
            paragraph.clear()  # Clear existing text

            # Add text before the placeholder
            if parts[0]:
                run = paragraph.add_run(parts[0])

            # Add the formatted variable value
            run = paragraph.add_run(value)
            if bold:
                run.bold = True
            if italic:
                run.italic = True
            if font_size:
                run.font.size = Pt(font_size)
            if color:
                run.font.color.rgb = RGBColor(*color)  # RGB tuple
            run.font.name = font_name
            # Add text after the placeholder
            if parts[1]:
                paragraph.add_run(parts[1])

    def write(self, vals):
        # logging.info(f"\n  >>>   vals: {vals} \n >>>  res: \n")
        if vals.get('contract_type_id', False):
            raise ValidationError(_("Contract Type cannot be updated as contract number is based on it."))
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # logging.info(f"\n >>>>> vals: {vals}\n")
            if not vals.get('name') or vals['name'] == _('New'):
                if not vals.get('contract_type_id'):
                    raise ValidationError(_("Please select a 'Contract Type'"))
                contract_type = self.env['hr.contract.type'].browse(int(vals.get('contract_type_id')))
                year = jdatejs()[0:4]

                contract_no = self.env['ir.sequence'].next_by_code('sd_hr.contracts.name') or _('New')
                vals['name'] = f"{contract_type.code}{year}/{contract_no}"
        return super().create(vals_list)

    def convert_docx_to_pdf(self, docx_path, temp_dir):
        subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", docx_path, '--outdir', temp_dir])

    def get_select(self, rec, field_name):
        field_name = dict(rec._fields[field_name]._description_selection(self.env)).get(rec[field_name])
        return field_name


class SdHrDocTemplate(models.Model):
    _name = 'sd_hr.doc_template'
    _description = "Keep contract type templates"

    variable_no = fields.Char(default=lambda self: _('New'))
    name = fields.Char(required=True)
    template_file = fields.Binary(string="Template File", required=True, attachment=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('variable_no') or vals['variable_no'] == _('New'):
                vals['variable_no'] = self.env['ir.sequence'].next_by_code('sd_hr.variables') or _('New')
        return super().create(vals_list)




