# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
class opp_rev_rpt_wiz(models.TransientModel):
    _name = 'opp.rev.rpt.wiz'
    
    product_group_id = fields.Many2one('od.product.group',string="Product Group")
    bdm_id = fields.Many2one('res.users',string="BDM")
    stage_id = fields.Many2one('crm.case.stage',string="Opp Stage")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    cost_centre_id = fields.Many2one('od.cost.centre',string="Cost Center")
    division_id = fields.Many2one('od.cost.division',string="Technology Unit")
    date_start = fields.Date(string="Date Start")
    date_end =fields.Date(string="Date End")
    
    @api.multi 
    def export_rpt(self):
        print "Exporting>>>>>>>>>>>>>>>>>>>>>>>>>>>"