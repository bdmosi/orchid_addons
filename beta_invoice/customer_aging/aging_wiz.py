# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning
class BetaCustomeAgingWiz(models.TransientModel):
    _name='beta.customer.aging.wiz'
    partner_ids = fields.Many2many('res.partner',string="Customer")
    branch_ids= fields.Many2many('od.cost.branch',string="Branch")
    date_start = fields.Date(string='Start Date',default=fields.Date.context_today)
    
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
    @api.multi 
    def export_rpt(self):
        wiz_id = self.id
        branch_ids = [pr.id for pr in self.branch_ids]
        partner_ids =[pr.id for pr in self.partner_ids]
        domain =[('account_id.type','=','receivable')]
        if branch_ids:
            domain +=[('od_branch_id','in',branch_ids)]
        if partner_ids:
            domain +=[('partner_id','in',partner_ids)]
            
        return {
            'domain': [('wiz_id','=',wiz_id)],
            'name': 'Customer Aging Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'beta.customer.aging.data',
            'type': 'ir.actions.act_window',
        }

class wiz_project_rpt_data(models.TransientModel):
    _name = 'beta.customer.aging.data'
    wiz_id = fields.Many2one('beta.customer.aging.wiz',string="Wizard")
    partner_id = fields.Many2one('res.partner',string="Customer")
    company_id = fields.Many2one('res.company',string="Company")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    bal1= fields.Float(string="0  -  30")
    bal2= fields.Float(string="30 -  60")
    bal3= fields.Float(string="60 -  90")
    bal4= fields.Float(string="90 - 120")
    bal5= fields.Float(string="  +120  ")
    balance = fields.Float(string="Balance")
    payment_term_id = fields.Many2one('account.payment.term',string="Payment Term")
    