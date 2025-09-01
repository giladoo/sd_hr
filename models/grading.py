from odoo import models, fields, api, _


class SdHrGrading(models.Model):
    _name = 'sd_hr.grading'
    _description = "sd_hr.grading"

    name = fields.Char(translate=True)
    sequence = fields.Integer(default=100)



