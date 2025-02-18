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
           _('Identification Id'),
           _('Gender'),
           _('Start Date'),
           _('Birth Day'),
           _('Birth Cert No'),
           _('Marital'),
           _('Children'),
           _('Father Name'),
           _('Work Mobile'),
           _('Private Address'),
           _('Place of Birth'),
           _('Bank Account no'),
           _('Bank Account Shaba'),
           ]
EMPLOYEE_FIELDS = ['barcode',
                   'name',
                   'identification_id',
                   'gender',
                   'start_date',
                   'birthday',
                   'birth_cert_no',
                   'marital',
                   'children',
                   'father_name',
                   'private_street',
                   'mobile_phone',
                   'place_of_birth',
                   'bank_account_no',
                   'bank_account_shaba',

                    ]




class PartnerXlsx(models.AbstractModel):
    _name = 'report.sd_hr.export_list'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, employees):
        sheet = workbook.add_worksheet(_('Employee List'))
        sheet.set_column(0, 30, 15)
        header_format = workbook.add_format({'bold': True})
        header_format.set_font_name('B Nazanin')
        row_format = workbook.add_format({'bold': False})
        row_format.set_font_name('B Nazanin')
        for col, header in enumerate(HEADERS):
            sheet.write(0, col, header, header_format)

        for row, employee in enumerate(employees):
            for col, rec in enumerate(EMPLOYEE_FIELDS):
                rec_data = employee[rec] if employee._fields.get(rec) else False
                value = ''
                if not rec_data:
                    value = ''
                elif rec_data and isinstance(rec_data, (date, datetime)):
                    # ic(rec_data)
                    value = jdatejs(rec_data)
                elif rec in ['gender', 'marital', 'certificate' ]:
                    value = dict(employee._fields[rec]._description_selection(self.env)).get(employee[rec])

                else:
                    value = rec_data

                sheet.write(row + 1, col, value, row_format)


        # sheet.autofit()

