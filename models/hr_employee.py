from odoo import models, fields, api, _
import zipfile
import io
from io import BytesIO
import base64
import os
from PIL import Image
import logging
from odoo.osv import expression
import json

class SdHrHrEmployee(models.Model):
    _inherit = 'hr.employee'

    certificate = fields.Selection(
        selection_add=[
            ('under_diploma', 'Under Diploma'),
            ('diploma', 'Diploma'),
            ('associate', 'Associate'),
    ],)

    # certificate = fields.Selection(
    #     selection_add=[('under_diploma', _('Under Diploma')),
    #     ('diploma', _('Diploma')),
    #     ('associate', _('Associate')),
    # ], translate=True)

    bank_name = fields.Char()
    bank_account_no = fields.Char()
    bank_account_shaba = fields.Char()
    bank_card_no = fields.Char()

    father_name = fields.Char(translate=True)
    personal_title = fields.Many2one('res.partner.title')
    birth_cert_no = fields.Char()
    birth_cert_s_1 = fields.Char()
    birth_cert_s_2 = fields.Char()
    birth_cert_s_3 = fields.Char()

    grading = fields.Many2one('sd_hr.grading')
    work_place_id = fields.Many2one('hr.work.place')
    cost_center = fields.Many2one('sd_hr.cost_center')


    def generate_barcode(self):
        self.barcode = self.env['ir.sequence'].next_by_code('sd_hr.employee.barcode') or ''
        # print(f"\n self: {self.name} {self.barcode}\n")

    def download_images(self):
        print(f"\ndownload_images: \n {self.env.context}")
        active_ids = self.env.context.get('active_ids', [])
        employees = self.browse(active_ids) if len(active_ids) > 0 else self
        attachment_model = self.env['ir.attachment']
        success_file = ''
        success_records = ''
        success_index = 0
        failed_file = ''
        failed_index = 0

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for rec in employees:
                img = rec.image_1920
                if rec.barcode and img and len(img) > 1000:
                    img = base64.b64decode(img)
                    img = Image.open(io.BytesIO(img))

                    width, height = img.size
                    pw = int(.19 * width)
                    ph = int(.1 * height)
                    box = (pw, ph, width - pw, height - ph)
                    img = img.crop(box)


                    img = img.resize((480, 640))

                    if img.mode == "RGBA":
                        img = img.convert("RGB")

                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG", quality=85)
                    img_bytes = buffer.getvalue()
                    index = 0
                    print(f"\n>>>>>>>>> {rec.barcode}")
                    while len(img_bytes) > 48000 and index < 50:
                        print(len(img_bytes))
                        buffer = io.BytesIO()
                        img.save(buffer, format="JPEG", quality=85 - index)
                        img_bytes = buffer.getvalue()
                        index += 5

                    file_name = rec.barcode.zfill(8)
                    zip_file.writestr(f"LF{file_name}.jpg", img_bytes)

                    success_file += f"{rec.barcode}  [{width}x{height}]  {rec.name}   \n"
                    success_records += f"{rec.barcode}\n"
                    success_index += 1

                else:
                    failed_file += f"{rec.barcode}    {rec.name}\n"
                    failed_index += 1
            failed_file = f"Failed Users: {failed_index}\n\n" + failed_file
            success_file = f"Success Users: {success_index}\n\n" + success_file

            zip_file.writestr(f"01-SuccessRecords.txt", success_records)
            zip_file.writestr(f"02-Success.txt", success_file)
            zip_file.writestr(f"03-Failed.txt", failed_file)


        zip_buffer.seek(0)
        zip_buffer = base64.b64encode(zip_buffer.getvalue()).decode('utf-8')

        # zip_buffer
        # logging.info(zip_buffer)
        attach_id = attachment_model.create({
            'res_model': self._name,
            'res_field': 'output_file',
            # 'res_id': self.id,
            'datas': zip_buffer,
            'name': 'image_file',
            'type': 'binary',
        })
        download_url = '/web/content/%s' % attach_id.id
        logging.info(f"\n >>>>>>>> download_url ZIP: {download_url}")

        return {'type': 'ir.actions.act_url',
                'url': download_url,
                'target': 'self',
                }




    # @api.depends('acc_number')
    # @api.depends_context('uid')
    # def _compute_user_has_group_validate_bank_account(self):
    #     user_has_group_validate_bank_account = self.env.user.has_group('account.group_validate_bank_account')
    #     for bank in self:
    #         bank.user_has_group_validate_bank_account = user_has_group_validate_bank_account

class SdHrHrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    bank_name = fields.Char()
    bank_account_no = fields.Char()
    bank_account_shaba = fields.Char()
    bank_card_no = fields.Char()

    father_name = fields.Char(translate=True)
    personal_title = fields.Many2one('res.partner.title')
    birth_cert_no = fields.Char()
    birth_cert_s_1 = fields.Char()
    birth_cert_s_2 = fields.Char()
    birth_cert_s_3 = fields.Char()

    grading = fields.Many2one('sd_hr.grading')
    cost_center = fields.Many2one('sd_hr.cost_center')



class SdHrHrContract(models.Model):
    _inherit = 'hr.contract'

    barcode = fields.Char(related='employee_id.barcode')
    work_location_id = fields.Many2one(related='employee_id.work_location_id')