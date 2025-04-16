from odoo import models, fields, api, _
from datetime import date

from odoo.api import depends
from icecream import ic

class SdHrHrEmployee(models.Model):
    _inherit = ['hr.employee']

    certificate = fields.Selection(selection_add=[
        ('under_diploma', _('Under Diploma')),
        ('diploma', _('Diploma')),
        ('associate', _('Associate')),
    ])

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

    age = fields.Integer(compute='_employee_age_calculation', default=0, store=True)

    contract_type = fields.Many2one('hr.contract.type')
    employment_start = fields.Date()
    contract_start = fields.Date()
    contract_end = fields.Date()
    employment_end = fields.Date()

    @api.depends('birthday')
    # @api.onchange('birthday')
    def _employee_age_calculation(self):
        end_date = fields.date.today()
        for rec in self:
            if isinstance(rec.birthday, fields.date) :
                rec.age =  end_date.year - rec.birthday.year - (
                        (end_date.month, end_date.day) < (rec.birthday.month, rec.birthday.day))

            # ic(rec.birthday, rec.age)

    def generate_barcode(self):
        self.barcode = self.env['ir.sequence'].next_by_code('sd_hr.employee.barcode') or ''
        # print(f"\n self: {self.name} {self.barcode}\n")

