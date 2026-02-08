# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SdHrPlanVersion(models.Model):
    _name = "sd_hr.plan_version"
    _description = "Plan Version"

    name = fields.Char( required=True, copy=False, readonly=False,
        default=lambda self: _('New'))
    # TODO:
    #   1) add sequence record
    #   2) prepare create function

    start_date = fields.Date(tracking=True)
    end_date = fields.Date( tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('ongoing', 'Ongoing'),
                              ('expired', 'Expired'), ],
                             requied=True, default='draft', tracking=True)

#     TODO: make sure there is only one ongoing version
    @api.onchange('state')
    def state_changed(self):
        pass
        # todo:
        #   1) if state is changed to ongoing, make the other ongoing record as expired
        #   2) change the version records of job_plan to this version based on publish date

    def generate_job_plans(self):
        # TODO:
        #   1) change the state to ongoing
        #   2) find the job_plan records which have record_date between start and end date of this version.
        #       Then change the version to this version
        #   3) create new job plans if they are not already exist for the date period
        print("!!!!!!!!!!!!!!!! You need to prepare this function!")
        ongoings = self.search([('state', '=', 'ongoing')])
        for rec in ongoings:
            rec.state = 'expired'
        self.state = 'ongoing'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            print(f"vals:{vals}")
            if vals.get('name', _('New')) == _('New'):

                name = self.env['ir.sequence'].next_by_code('sd_hr.plan_version')
                print(f"vals get:{name}")

                vals['name'] = name or _("New")
        print(f">>>>>>>>>>>>> vals_list: {vals_list}")
        return super().create(vals_list)


class SdHrJobPlan(models.Model):
    _name = "sd_hr.job_plan"
    _description = "Job Plan"

    version = fields.Many2one("sd_hr.plan_version")
    record_date = fields.Date()
    job_id = fields.Many2one("hr.job")
    plan = fields.Integer()
    actual = fields.Integer()
    # TODO: it must calculated while the job's employee count is changed.
    #  note: only if the change month is the same as record's date month
    #  it needs a write and create super function on hr.employee module






















