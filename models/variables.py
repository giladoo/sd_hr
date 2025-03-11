from odoo import models, fields, api, _

class SdHrVariables(models.Model):
    _name = 'sd_hr.variables'
    _description = "Keep odoo variables"
    _rec_name = "variable"


    model_id = fields.Many2one('ir.model', required=True, ondelete="cascade")
    model_res_id = fields.Integer( required=True,)
    variable = fields.Char( copy=False)
    value_source = fields.Selection([('text', 'Text'), ('function', 'Function'),],
                                        default='function', required=True)
    value_type = fields.Selection([('text', 'Text'), ('number', 'Number'), ('html', 'HTML'),],
                                        default="text", required=True)
    value_text = fields.Text(copy=False)
    value_function = fields.Text(copy=False)
    value_fonts = fields.Selection([('b_nazanin', 'B Nazanin'),
                                    ('b_titr', 'B Titr'),
                                    ('b_zar', 'B Zar'),
                                    ('b_yagut', 'B Yagut'),
                                    ('b_yekan', 'B Yekan'),
                                    ('arial', 'Arial'),
                                    ], required=True, default='b_nazanin')
