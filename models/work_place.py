from odoo import models, fields, api

class SdHrWorkPlace(models.Model):
    _name = "hr.work.place"
    _description = "Hr Work Place"

    name = fields.Char(required=True)
    location_id = fields.Many2one('hr.work.location', required=True)
    sequence = fields.Integer(default=100)