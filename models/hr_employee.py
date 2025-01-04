from odoo import models, fields, api, _


class SdHrHrEmployee(models.Model):
    _inherit = 'hr.employee'

    project_name = fields.Many2one('sd_projects.projects')
    father_name = fields.Char(translate=True)
    personal_title = fields.Many2one('res.partner.title')
    birth_cert_no = fields.Char()
    birth_cert_s_1 = fields.Char()
    birth_cert_s_2 = fields.Char()
    birth_cert_s_3 = fields.Char()

