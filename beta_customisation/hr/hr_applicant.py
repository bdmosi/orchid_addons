# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
class hr_applicant(models.Model):
    _inherit = "hr.applicant"
    beta_join_id = fields.Many2one('od.beta.joining.form',string="Beta Joining Form")
    