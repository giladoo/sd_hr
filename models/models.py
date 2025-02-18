from odoo import models, fields, api, _
from datetime import date

from odoo.api import depends
from icecream import ic

class SdHrExport(models.Model):
    _name = 'sd_hr.export'
    _description = 'sd_hr.export'


    def export_list(self):

        active_ids = self.env.context.get('active_ids')
        ic(active_ids)

        employees = self.env['hr.employee'].browse(active_ids)
