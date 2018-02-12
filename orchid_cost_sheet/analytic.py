# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class account_analytic_account(models.Model):
    _inherit = "account.analytic.account"
    od_cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet",readonly=True)

    od_cost_centre_id =fields.Many2one('od.cost.centre',string='Cost Centre',related="od_cost_sheet_id.od_cost_centre_id",readonly=True,store=True)
    od_branch_id =fields.Many2one('od.cost.branch',string='Branch',related="od_cost_sheet_id.od_branch_id",readonly=True,store=True)
    od_division_id = fields.Many2one('od.cost.division',string='Division',related="od_cost_sheet_id.od_division_id",readonly=True,store=True)
    lead_id = fields.Many2one('crm.lead',string="Opportunity",related="od_cost_sheet_id.lead_id",readonly=True)
    
    od_manual = fields.Boolean("Manual Link")
    cost_centre_id =fields.Many2one('od.cost.centre',string='M Cost Centre')
    branch_id =fields.Many2one('od.cost.branch',string='M Branch')
    division_id = fields.Many2one('od.cost.division',string='M Division')
   
    op_stage_id = fields.Many2one('crm.case.stage',string="Opp Stage",related="lead_id.stage_id",readonly=True)    
    op_expected_booking = fields.Date(string="Opp Expected Booking",related="lead_id.date_action",readonly=True)    
    sale_team_id = fields.Many2one('crm.case.section',string="Sale Team",related="lead_id.section_id",readonly=True)
    op_stage_id = fields.Many2one('crm.case.stage',string="Opp Stage",related="lead_id.stage_id",readonly=True)    
    fin_approved_date = fields.Datetime(string="Finance Approved Date",related="od_cost_sheet_id.approved_date",readonly=True)
    od_closing_date = fields.Date(string="Closing Date")

class project_project(models.Model):
    _inherit ='project.project'


    @api.one
    def od_get_sales_order_count(self):
        sale_order = self.env['sale.order']
        analytic_id = self.analytic_account_id and self.analytic_account_id.id
        domain =[('project_id','=',analytic_id)]
        count =len(sale_order.search(domain))
        self.od_sale_count = count
    od_sale_count = fields.Integer(string="Sales Orders",compute="od_get_sales_order_count")
    od_cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet",readonly=True,related="analytic_account_id.od_cost_sheet_id")

    technical_consultant1_id = fields.Many2one('res.users',string="Technical Consultant 1")
    technical_consultant2_id = fields.Many2one('res.users',string="Technical Consultant 2")
    @api.multi
    def od_open_sales_order(self):
        sales_order = self.env['sale.order']
        analytic_id = self.analytic_account_id and self.analytic_account_id.id
        domain = [('project_id','=',analytic_id)]
        sales = sales_order.search(domain)
        sale_ids = [sale.id for sale in sales]
        dom = [('id','in',sale_ids)]
        return {
            'domain':dom,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
        }
