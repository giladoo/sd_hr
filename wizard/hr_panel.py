from odoo import models, fields, api, _
import json

from odoo.exceptions import ValidationError


class SdHrPanel(models.TransientModel):
    _name = 'sd_hr.panel'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', default=lambda self: self.env.context.get('default_employee_id', False))
    employee_name = fields.Char(related='employee_id.name')
    job_title = fields.Char(related='employee_id.job_title')
    department = fields.Many2one(related='employee_id.department_id')
    identification_id = fields.Char(related='employee_id.identification_id')
    birthday = fields.Date(related='employee_id.birthday')
    gender = fields.Selection(related='employee_id.gender')
    image_1920 = fields.Image(related='employee_id.image_1920')
    # relatives_1 = fields.One2many('sd_hr_relatives.members', 'employee_id' )
    employee_user_id = fields.Html()
    relatives = fields.Many2many('sd_hr_relatives.members', domain="[('employee_id', '=', employee_id)]" )

    documents = fields.Many2many('sd_hr_documents.attachments', domain="[('employee_id', '=', employee_id)]" )
    documents_count = fields.Integer(compute='_documents_count', store=False)

    helper_field = fields.Boolean(default=True, compute='_compute_helper_field')
    # @api.onchange('documents')
    @api.onchange('employee_id')
    def _documents_count(self):
        documents_model = self.env['sd_hr_documents.attachments']
        relatives_model = self.env['sd_hr_relatives.members']
        domain = [('employee_id', '=', self.employee_id.id)]

        self.documents = documents_model.search(domain)
        self.documents_count = documents_model.sudo().search_count(domain)
        self.relatives = relatives_model.search(domain)

    @api.depends('relatives')
    def _compute_helper_field(self):
        print(f"\n RELATIVES documents: {self.documents}")
        self.helper_field = not self.helper_field
        documents_model = self.env['sd_hr_documents.attachments']
        domain = [('employee_id', '=', self.employee_id.id)]
        #
        # self.documents = documents_model.search(domain)
        self.documents_count = documents_model.sudo().search_count(domain)

    def employee_action_view(self):
        if self.employee_id:
            view_id = self.env.ref('hr.view_employee_form').sudo().read()[0]
            domain = []
            context = {}
            return {
                'name': _('Documents'),
                'domain': domain,
                'res_model': 'hr.employee',
                'type': 'ir.actions.act_window',
                'res_id': self.employee_id.id,
                'view_id': False,
                'view_mode': 'form',
                'context': context
            }
        else:
            return {}


    def employee_action_document_view(self):
        action =False
        return action

