# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp
from operator import div
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
        product_group_id = self.product_group_id and self.product_group_id.id or False
        bdm_id = self.bdm_id and self.bdm_id.id or False
        stage_id = self.stage_id and self.stage_id.id or False
        branch_id = self.branch_id and self.branch_id.id or False
        cost_centre_id = self.cost_centre_id and self.cost_centre_id.id or False
        division_id = self.division_id and self.division_id.id or False
        date_start = self.date_start
        date_end =self.date_end 
        wiz_id = self.id
        domain = []
        if bdm_id:
            domain += [('business_development','=',bdm_id)]
        if stage_id:
            domain += [('op_stage_id','=',stage_id)]
        if branch_id:
            domain += [('od_branch_id','=',branch_id)]
        if cost_centre_id:
            domain += [('od_cost_centre_id','=',cost_centre_id)]
        if division_id:
            domain += [('od_division_id','=',division_id)]
        if date_start:
            domain += [('op_expected_booking','>=',date_start)]
        if date_end:
            domain += [('op_expected_booking','<=',date_end)]
            
        cost_sheet_data = self.env['od.cost.sheet'].search(domain) 
        result =[]
        for sheet in cost_sheet_data:
            sheet_id = sheet.id
            opp_id = sheet.lead_id and sheet.lead_id.id 
            expected_booking = sheet.op_expected_booking 
            stage_id = sheet.op_stage_id and sheet.op_stage_id.id
            for line in sheet.summary_weight_line:
                
                if product_group_id:
                    if line.pdt_grp_id.id == product_group_id:
                        result.append((0,{
                            'wiz_id':wiz_id,
                            'cost_sheet_id':sheet_id, 
                            'opp_id':opp_id ,
                            'expected_booking':expected_booking,
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
                    result.append((0,{
                            'wiz_id':wiz_id,
                            'cost_sheet_id':sheet_id, 
                            'opp_id':opp_id ,
                            'expected_booking':expected_booking,
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
        
        if result:
            self.env['wiz.rev.rpt.data'].create(result)
        return {
            'domain': [('wiz_id','=',wiz_id)],
            'name': 'Revenue Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'wiz.rev.rpt.data',
            'type': 'ir.actions.act_window',
        }
                        
        
        
        

class wiz_rev_rpt(models.TransientModel):
    _name = 'wiz.rev.rpt.data'
    wiz_id = fields.Integer(string="Wizard")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    opp_id = fields.Many2one('crm.lead',string='Opportunity')
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