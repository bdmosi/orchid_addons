# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp

class opp_rev_sale_in_wiz(models.TransientModel):
    _name = 'opp.sale.in.rpt.wiz'
    
    
    
    created_by_ids = fields.Many2many('res.users',string="Created By")
    product_group_ids = fields.Many2many('od.product.group',string="Product Group")
    
    
    branch_ids= fields.Many2many('od.cost.branch',string="Branch")
    cost_centre_ids = fields.Many2many('od.cost.centre',string="Cost Center")
    division_ids = fields.Many2many('od.cost.division',string="Technology Unit")
    
    date_start = fields.Date(string="Approved Date Start")
    date_end =fields.Date(string="Approved Date End")
    
    wiz_line = fields.One2many('wiz.sale.in.data','wiz_id',string="Wiz Line")
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    @api.multi 
    def export_rpt(self):
       
        
        product_group_ids = [pr.id for pr in self.product_group_ids]
        created_by_ids = [pr.id for pr in self.created_by_ids]
        
        branch_ids = [pr.id for pr in self.branch_ids]
        cost_centre_ids = [pr.id for pr in self.cost_centre_ids]
        division_ids = [pr.id for pr in self.division_ids]
        
        
        date_start = self.date_start
        date_end =self.date_end 
        wiz_id = self.id
        company_id = self.company_id and self.company_id.id 
        domain = [('status','=','active'),('state','in',('approved','done','modify','change','analytic_change','change_processed','redistribution_processed'))]
        if company_id:
            domain += [('company_id','=',company_id)]
        if created_by_ids:
            domain += [('lead_created_by','in',created_by_ids)]
        
        if branch_ids:
            domain += [('od_branch_id','in',branch_ids)]
        if cost_centre_ids:
            domain += [('od_cost_centre_id','in',cost_centre_ids)]
        if division_ids:
            domain += [('od_division_id','in',division_ids)]
        if date_start:
            domain += [('approved_date','>=',date_start)]
        if date_end:
            domain += [('approved_date','<=',date_end)]
            
        cost_sheet_data = self.env['od.cost.sheet'].search(domain) 
        result =[]
        for sheet in cost_sheet_data:
            sheet_id = sheet.id
            opp_id = sheet.lead_id and sheet.lead_id.id 
            date = sheet.approved_date 
            stage_id = sheet.op_stage_id and sheet.op_stage_id.id
            bdm_user_id = sheet.lead_created_by and sheet.lead_created_by.id
            for line in sheet.summary_weight_line:
                
                if product_group_ids:
                    if line.pdt_grp_id.id in product_group_ids:
                        result.append((0,0,{
                            'wiz_id':wiz_id,
                            'cost_sheet_id':sheet_id, 
                            'opp_id':opp_id ,
                            'bdm_user_id':bdm_user_id ,
                            'date':date,
                            'stage_id':stage_id,
                            'pdt_grp_id':line.pdt_grp_id and line.pdt_grp_id.id,
                            'total_sale':line.total_sale,
                            'disc':line.disc,
                            'sale_aftr_disc':line.sale_aftr_disc,
                            'total_cost':line.total_cost,
                            'profit':line.profit,
                            'manpower_cost':line.manpower_cost,
                            'total_gp':line.total_gp
                            }))
                else:
                    result.append((0,0,{
                            'wiz_id':wiz_id,
                            'cost_sheet_id':sheet_id, 
                            'opp_id':opp_id ,
                            'bdm_user_id':bdm_user_id,
                            'date':date,
                            'stage_id':stage_id,
                            'pdt_grp_id':line.pdt_grp_id and line.pdt_grp_id.id,
                            'total_sale':line.total_sale,
                            'disc':line.disc,
                            'sale_aftr_disc':line.sale_aftr_disc,
                            'total_cost':line.total_cost,
                            'profit':line.profit,
                            'manpower_cost':line.manpower_cost,
                            'total_gp':line.total_gp
                            }))        
        
        self.write({'wiz_line':result})
        return {
            'domain': [('wiz_id','=',wiz_id)],
            'name': 'Revenue Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'wiz.sale.in.data',
            'type': 'ir.actions.act_window',
        }
                        
        
        
        

class wiz_sale_in_rpt(models.TransientModel):
    _name = 'wiz.sale.in.data'
    wiz_id = fields.Many2one('opp.sale.in.rpt.wiz',string="Wizard")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    opp_id = fields.Many2one('crm.lead',string='Opportunity')
    bdm_user_id = fields.Many2one('res.users',string="Lead/Opp Created By")
    date = fields.Datetime(string="Approved Date")
    stage_id = fields.Many2one('crm.case.stage',string="Opp Stage")
    pdt_grp_id = fields.Many2one('od.product.group',string='Product Group')
    total_sale = fields.Float(string="Sales",digits=dp.get_precision('Account'))
    disc = fields.Float(string="Disc %",digits=dp.get_precision('Account'))
    sale_aftr_disc = fields.Float(string="Sales After Disc",digits=dp.get_precision('Account'))
    total_cost = fields.Float(string="Cost",digits=dp.get_precision('Account'))
    profit = fields.Float(string="Profit",digits=dp.get_precision('Account'))
    manpower_cost = fields.Float(string="Manpower Cost",digits=dp.get_precision('Account'))
    total_gp = fields.Float(string="Total GP",digits=dp.get_precision('Account'))
    
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