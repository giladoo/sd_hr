from odoo import models, fields, api, _


class SdHrHrEmployee(models.Model):
    _inherit = 'hr.employee'

    project_name = fields.Many2one('hr.employee.project_name')
    father_name = fields.Char(translate=True)
    personal_title = fields.Many2one('res.partner.title')



class SdHrHrEmployeeProjectName(models.Model):
    _name = 'hr.employee.project_name'
    _description = 'HR Projects Name'

    name = fields.Char(required=True, translate=True)