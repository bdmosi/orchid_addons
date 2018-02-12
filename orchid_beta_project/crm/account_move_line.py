# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
class account_move_line(models.Model):
    _inherit = "account.move.line"
    od_opp_id = fields.Many2one('crm.lead',string="Opportunity")
