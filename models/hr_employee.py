from odoo import models, fields, api, _


class SdHrHrEmployee(models.Model):
    _inherit = 'hr.employee'

    certificate = fields.Selection(
        selection_add=[('under_diploma', 'Under Diploma'),
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