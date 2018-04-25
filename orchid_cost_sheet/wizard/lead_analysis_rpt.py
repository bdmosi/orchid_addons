# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp

class lead_analysis_rpt_wiz(models.TransientModel):
    _name = 'lead.analysis.rpt.wiz'
    name = fields.Char(string="Name",required=True)
       
    created_by_ids = fields.Many2many('res.users',string="Created By")
    stage_ids = fields.Many2many('crm.case.stage',string="Opp Stage",domain=[('id','!=',6)])    
    branch_ids= fields.Many2many('od.cost.branch',string="Branch")
    date_start = fields.Date(string="Expected Booking Date Start")
    date_end =fields.Date(string="Expected Booking Date End")
    lead_date_start = fields.Date(string="Created On Start")
    lead_date_end =fields.Date(string="Created On End")
    sm_ids = fields.Many2many('res.users','wiz_sale_a','wiz_id','user_id',string="Sales Account Manager")
    wiz_line = fields.One2many('wiz.lead.analysis.data','wiz_id',string="Wiz Line")

    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    @api.multi 
    def export_rpt(self):
        created_by_ids = [pr.id for pr in self.created_by_ids]
        stage_ids = [pr.id for pr in self.stage_ids]
        branch_ids = [pr.id for pr in self.branch_ids]
        sm_ids = [pr.id for pr in self.sm_ids]
        date_start = self.date_start
        date_end =self.date_end
        lead_date_start = self.lead_date_start
        lead_date_end =self.lead_date_end 
        wiz_id = self.id
        company_id = self.company_id and self.company_id.id 
        domain = [('status','=','active')]
        if company_id:
            domain += [('company_id','=',company_id)]
        if created_by_ids:
            domain += [('create_uid','in',created_by_ids)]
        if stage_ids:
            domain += [('stage_id','in',stage_ids)]
       
        if branch_ids:
            domain += [('od_branch_id','in',branch_ids)]
       
                    
        if sm_ids:
            domain += [('user_id','in',sm_ids)]
        
        if date_start:
            domain += [('date_action','>=',date_start)]
        if date_end:
            domain += [('date_action','<=',date_end)]
        
        if lead_date_start:
            domain += [('create_date','>=',lead_date_start)]
        if lead_date_end:
            domain += [('create_date','<=',lead_date_end)]
            
        lead_data = self.env['crm.lead'].search(domain) 
        result =[]
        for lead in lead_data:
            
            opp_id = lead.id
            name = lead.name 
            created_on = lead.create_date
            created_by_id = lead.create_uid and lead.create_uid.id 
            expected_booking = lead.date_action 
            stage_id = lead.stage_id and lead.stage_id.id 
            partner_id = lead.partner_id and lead.partner_id.id 
            company_id = lead.company_id and lead.company_id.id 
            branch_id = lead.od_branch_id and lead.od_branch_id.id
            division_id = lead.od_division_id and lead.od_division_id.id
            sam_id = lead.user_id and lead.user_id.id
            type = lead.type 
            cost_sheet = self.env['od.cost.sheet'].search([('lead_id','=',lead.id),('status','=','active')],limit=1)
            sheet_id = cost_sheet and cost_sheet.id
            mp_sales = cost_sheet and cost_sheet.a_total_manpower_sale or 0.0
            profit_mp =0.0
            if cost_sheet:
                profit_mp = cost_sheet.sum_profit + cost_sheet.a_total_manpower_cost
            result.append((0,0,{
                                'wiz_id':wiz_id,
                                'cost_sheet_id':sheet_id, 
                                 'expected_booking':expected_booking,
                                'opp_id':opp_id ,
                                'name':name,
                                'partner_id':partner_id,
                                'company_id':company_id,
                                'branch_id':branch_id,
                                'created_on':created_on,
                                'created_by_id':created_by_id,
                                'division_id':division_id,
                                'type':type,
                                'stage_id':stage_id,
                                'cs_sale':lead.od_costsheet_sale,
                                 'mp_sales':mp_sales,
                                 'sam_id':sam_id,
                                'profit_mp':profit_mp,
                                }))
        
        self.wiz_line.unlink()
        self.write({'wiz_line':result})
        return {
            'domain': [('wiz_id','=',wiz_id)],
            'name': 'Lead Analysis',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'wiz.lead.analysis.data',
            'type': 'ir.actions.act_window',
        }
                        
        
        
        

class wiz_lead_analysis_rpt(models.TransientModel):
    _name = 'wiz.lead.analysis.data'
    wiz_id = fields.Many2one('lead.analysis.rpt.wiz',string="Wizard")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Active Cost Sheet',)
    opp_id = fields.Many2one('crm.lead',string='Opportunity')
    name = fields.Char(string="Name")
    type = fields.Selection([('lead','Lead'),('opportunity','Opportunity')],string="Type")
    created_on = fields.Datetime(string="Created On")
    partner_id = fields.Many2one('res.partner',string="Customer")
    created_by_id = fields.Many2one('res.users',string="Lead/Opp Created By")
    expected_booking = fields.Date(string="Opp Expected Booking")
    submitted_on =fields.Date(string="Submitted To Customer")
    stage_id = fields.Many2one('crm.case.stage',string="Opp Stage")
    cs_sale = fields.Float(string="CS Sales",digits=dp.get_precision('Account'))
    profit_mp = fields.Float(string="Profit With MP",digits=dp.get_precision('Account'))
    mp_sales = fields.Float(string="MP Sales")
    branch_id =  fields.Many2one('od.cost.branch',string="Branch")
    division_id =  fields.Many2one('od.cost.division',string="Technology Unit")
    sam_id = fields.Many2one('res.users',string="Sales Account Manager")
    company_id = fields.Many2one('res.company',string="Company")
    @api.multi
    def btn_open_opp(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'crm.lead',
                'res_id':self.opp_id and self.opp_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    @api.multi
    def btn_open_cost(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',
                }

