# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api , _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import pytz
from  jdatetimext import jdatejs
from odoo import http
from icecream import ic
HEADERS = [_('Employee No'),
           _('Name'),
           _('Father Name'),
           _('Identification Id'),
           _('Gender'),
           _('Start Date'),
           _('Birth Day'),
           _('Birth Cert No'),
           _('SSN ID'),
           _('Marital'),
           _('Children'),
           _('Private Address'),
           _('Work Mobile'),
           _('Place of Birth'),
           _('Bank Name'),
           _('Bank Account no'),
           _('Bank Account Shaba'),
           ]
EMPLOYEE_FIELDS = ['barcode',
                   'name',
                   'father_name',
                   'identification_id',
                   'gender',
                   'start_date',
                   'birthday',
                   'birth_cert_no',
                   'ssnid',
                   'marital',
                   'children',
                   'private_street',
                   'mobile_phone',
                   'place_of_birth',
                   'bank_name',
                   'bank_account_no',
                   'bank_account_shaba',

                    ]




class PartnerXlsx(models.AbstractModel):
    _name = 'report.sd_hr.export_list'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, employees):
        sheet = workbook.add_worksheet(_('Employee List'))
        sheet.right_to_left()
        # sheet.set_column(0, 30, 15)

        header_format = workbook.add_format({'font_name': "B Nazanin", 'bold': True, 'align': 'center','color': "#ffffff", 'fg_color': "#888888"})
        header_format.set_font('B Nazanin')
        header_format.set_font_family(0)
        header_format.set_font_charset(178)

        row_format = workbook.add_format({'font_name': "B Nazanin", 'align': 'center',})
        row_format.set_font('B Nazanin')
        row_format.set_font_family(0)
        row_format.set_font_charset(178)

        for col, header in enumerate(HEADERS):
            sheet.write(0, col, _(header), header_format)
        all_records = []
        for row, employee in enumerate(employees):
            records = {}
            for col, rec in enumerate(EMPLOYEE_FIELDS):
                rec_data = employee[rec] if employee._fields.get(rec) else False
                value = ''

                if not rec_data:
                    if rec in ['children']:
                        value = 0
                    else:
                        value = ''
                elif rec_data and isinstance(rec_data, (date, datetime)):
                    # ic(rec_data)
                    value = jdatejs(rec_data)
                elif rec in ['gender', 'marital', 'certificate' ]:
                    value = dict(employee._fields[rec]._description_selection(self.env)).get(employee[rec])

                else:
                    value = rec_data
                records[rec] = value


                sheet.write(row + 1, col, value)
            all_records.append(records)

        ic(all_records)
        for i, rec in enumerate(EMPLOYEE_FIELDS):
            rec_len = max(list([len(str(r[rec]).strip()) for r in all_records]) + [len(str(rec))])
            sheet.set_column(i, i, rec_len + 2, row_format)

        # sheet.autofit()

