from odoo import models, fields, api, _


class SdHrCostCenter(models.Model):
    _name = 'sd_hr.cost_center'

    name = fields.Char(translate=True)
    sequence = fields.Integer(default=100)



