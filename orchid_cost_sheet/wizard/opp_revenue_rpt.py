# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp

class opp_rev_rpt_wiz(models.TransientModel):
    _name = 'opp.rev.rpt.wiz'
    
    bdm_id = fields.Many2one('res.users',string="BDM")
    product_group_id = fields.Many2one('od.product.group',string="Product Group")
    stage_id = fields.Many2one('crm.case.stage',string="Opp Stage")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    cost_centre_id = fields.Many2one('od.cost.centre',string="Cost Center")
    division_id = fields.Many2one('od.cost.division',string="Technology Unit")
    
    created_by_ids = fields.Many2many('res.users',string="Created By")
    product_group_ids = fields.Many2many('od.product.group',string="Product Group")
    stage_ids = fields.Many2many('crm.case.stage',string="Opp Stage",domain=[('id','!=',6)])
#     stage = fields.Selection([(1,'Approved'),(4,'Design Ready'),(12,'Pipeline'),(5,'Commit'),(6,'Lost'),(8,'Cancelled')],string="Opp Stage")
    
    branch_ids= fields.Many2many('od.cost.branch',string="Branch")
    cost_centre_ids = fields.Many2many('od.cost.centre',string="Cost Center")
    division_ids = fields.Many2many('od.cost.division',string="Technology Unit")
    
    date_start = fields.Date(string="Expected Booking Date Start")
    date_end =fields.Date(string="Expected Booking Date End")
    
    wiz_line = fields.One2many('wiz.rev.rpt.data','wiz_id',string="Wiz Line")
    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    @api.multi 
    def export_rpt(self):
        product_group_id = self.product_group_id and self.product_group_id.id or False
        bdm_id = self.bdm_id and self.bdm_id.id or False
        stage_id = self.stage_id and self.stage_id.id or False
        branch_id = self.branch_id and self.branch_id.id or False
        cost_centre_id = self.cost_centre_id and self.cost_centre_id.id or False
        division_id = self.division_id and self.division_id.id or False
        
        product_group_ids = [pr.id for pr in self.product_group_ids]
        created_by_ids = [pr.id for pr in self.created_by_ids]
        stage_ids = [pr.id for pr in self.stage_ids]
        branch_ids = [pr.id for pr in self.branch_ids]
        cost_centre_ids = [pr.id for pr in self.cost_centre_ids]
        division_ids = [pr.id for pr in self.division_ids]
        
        
        date_start = self.date_start
        date_end =self.date_end 
        wiz_id = self.id
        company_id = self.company_id and self.company_id.id 
        domain = [('status','=','active')]
        if company_id:
            domain += [('company_id','=',company_id)]
        if created_by_ids:
            domain += [('lead_created_by','in',created_by_ids)]
        if stage_ids:
            domain += [('op_stage_id','in',stage_ids)]
        if not stage_ids:
            domain += [('op_stage_id','!=',6)]
        if branch_ids:
            domain += [('od_branch_id','in',branch_ids)]
        if cost_centre_ids:
            domain += [('od_cost_centre_id','in',cost_centre_ids)]
        if division_ids:
            domain += [('od_division_id','in',division_ids)]
        if date_start:
            domain += [('op_expected_booking','>=',date_start)]
        if date_end:
            domain += [('op_expected_booking','<=',date_end)]
            
        cost_sheet_data = self.env['od.cost.sheet'].search(domain) 
        result =[]
        for sheet in cost_sheet_data:
            sheet_id = sheet.id
            opp_id = sheet.lead_id and sheet.lead_id.id 
            date = sheet.approved_date 
            stage_id = sheet.op_stage_id and sheet.op_stage_id.id
            bdm_user_id = sheet.lead_created_by and sheet.lead_created_by.id
            partner_id = sheet.od_customer_id and sheet.od_customer_id.id 
            company_id = sheet.company_id and sheet.company_id.id 
            branch_id = sheet.od_branch_id and sheet.od_branch_id.id
            if product_group_ids:
                for line in sheet.summary_weight_line:
                    if product_group_ids:
                        if line.pdt_grp_id.id in product_group_ids:
                            result.append((0,0,{
                                'wiz_id':wiz_id,
                                'cost_sheet_id':sheet_id, 
                                'opp_id':opp_id ,
                                'partner_id':partner_id,
                                'company_id':company_id,
                                'branch_id':branch_id,
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
                                'partner_id':partner_id,
                                'company_id':company_id,
                                'branch_id':branch_id,
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
            else:
                result.append((0,0,{
                                'wiz_id':wiz_id,
                                'cost_sheet_id':sheet_id, 
                                'opp_id':opp_id ,
                                'partner_id':partner_id,
                                'company_id':company_id,
                                'branch_id':branch_id,
                                'bdm_user_id':bdm_user_id,
                                'date':date,
                                'stage_id':stage_id,
                                'pdt_grp_id':False,
                                'total_sale':sheet.sum_tot_sale,
                                'disc':abs(sheet.special_discount),
                                'sale_aftr_disc':sheet.sum_total_sale,
                                'total_cost':sheet.sum_tot_cost,
                                'profit':sheet.sum_profit,
                                'manpower_cost':sheet.a_total_manpower_cost,
                                'total_gp':sheet.sum_profit + sheet.a_total_manpower_cost
                                }))
        
        self.write({'wiz_line':result})
        return {
            'domain': [('wiz_id','=',wiz_id)],
            'name': 'Pipeline Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'wiz.rev.rpt.data',
            'type': 'ir.actions.act_window',
        }
                        
        
        
        

class wiz_rev_rpt(models.TransientModel):
    _name = 'wiz.rev.rpt.data'
    wiz_id = fields.Many2one('opp.rev.rpt.wiz',string="Wizard")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    opp_id = fields.Many2one('crm.lead',string='Opportunity')
    bdm_user_id = fields.Many2one('res.users',string="Lead/Opp Created By")
    expected_booking = fields.Date(string="Opp Expected Booking")
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