from odoo import models, fields, api, _
import json

from odoo.exceptions import ValidationError
from openpyxl import load_workbook
import base64
import io


class SdHrEmployeeImport(models.TransientModel):
    _name = 'sd_hr.employee_import'
    _description = "sd_hr.employee_import"


    excel_file = fields.Binary(required=True)
    excel_file_name = fields.Char()


    def import_file(self):
        read_form = self.read()[0]
        employee_model = self.env['hr.employee']
        if read_form.get('excel_file'):
            if self.excel_file and self.excel_file_name and (self.excel_file_name.split('.')[-1]).lower() in ['xlsx',
                                                                                                              'xlsm']:
                try:
                    excel_file = base64.b64decode(self.excel_file)
                    report_file = io.BytesIO(excel_file)
                    xlsx = load_workbook(filename=report_file, data_only=True)
                    sheet = xlsx.worksheets[0]
                    sheet_values = list(sheet.values)
                    emp_fields = employee_model._fields
                    print(f"  >>>>>>\n{emp_fields}\n  <<<<<<<<")

                    # for row, values in expected_values.items():
                    #     row_values = [v if v is not None else '' for v in sheet_values[row]]
                    #     for row_value, expected_value in zip(row_values, values):
                    #         self.assertEqual(row_value, expected_value)
                    print(f"  >>>>>>\n{sheet_values}\n  <<<<<<<<")
                except:
                    pass
            else:
                raise ValidationError(_('Upload an Excel file, xlsx extension.'))