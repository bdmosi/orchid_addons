# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class crm_lead(models.Model):
    _inherit = 'crm.lead'
    _rec_name = 'od_number'

    
    def get_line_manager_email(self,cr,uid,user_id,context={}):
        hr_obj = self.pool.get('hr.employee')
        hr_emp_id = hr_obj.search(cr,uid,[('user_id','=',user_id)],limit=1)
        hr_brw_ob = hr_obj.browse(cr,uid,hr_emp_id)
        mgr_user_email= hr_brw_ob.parent_id and hr_brw_ob.parent_id.user_id and hr_brw_ob.parent_id.user_id.login or ''
        return mgr_user_email
    
    @api.one
    def _compute_count(self):
        for obj in self:
            sheet_ids = self.env['od.cost.sheet'].search([('lead_id','=',obj.id)])
            if sheet_ids:
                self.od_costsheet_count = len(sheet_ids)


    @api.one
    def get_vals(self):
        cost_sheet = self.env['od.cost.sheet']
        lead_id = self.id
        domain = [('lead_id','=',lead_id),('state','!=','draft'),('status','in',('active','baseline'))]
        sheet = cost_sheet.search(domain,limit=1)
        if sheet:
            self.od_costsheet_sale = sheet.sum_total_sale
            self.od_costsheet_cost = sheet.sum_tot_cost
            profit = sheet.sum_profit
#             manpower_cost = sheet.calculate_total_manpower_cost()
#             new_profit = profit + manpower_cost
            self.od_costsheet_profit = profit
#             self.od_costsheet_manpower_cost = manpower_cost
#             self.od_costsheet_new_profit = new_profit
#             sale = sheet.sum_total_sale
            self.od_costsheet_profit_percent = sheet.sum_profit_per
#             if sale:
#                 self.od_costsheet_new_profit_percent = (new_profit/sale) * 100.0
            
           
    
    
    
#     @api.one 
#     @api.onchange('od_responsible_id')
#     def onchange_od_responsible_id(self):
#         print "onchange>>>>>>>>>>>FFFD",self.od_responsible_id
#         if self.od_responsible_id:
#             sheet_pool = self.env['od.cost.sheet']
#             sheets = sheet_pool.search([('lead_id','=',self.id)])
#             print "sheets>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",sheets,self.od_responsible_id.id
#             for sheet in sheets:
#                 sheet.write({'pre_sales_engineer':self.od_responsible_id.id})
            
    
    
    od_cost_sheet_line = fields.One2many('od.cost.sheet','lead_id',string='Cost Sheet Lines')
    od_number = fields.Char(string='Number',readonly="1",default='/')
    od_costsheet_count  = fields.Integer(string='Count',compute="_compute_count")
    od_costsheet_sale = fields.Float('Total Sale',compute="get_vals")
    od_costsheet_cost = fields.Float('Total Cost',compute="get_vals")
    od_costsheet_profit = fields.Float('Profit',compute="get_vals")
    od_costsheet_new_profit = fields.Float('New Profit',)
    od_costsheet_new_profit_percent = fields.Float('New Profit Percentage')
    od_costsheet_manpower_cost = fields.Float('Manpower Cost')
    od_costsheet_profit_percent = fields.Float('Profit Percentage',compute="get_vals")
    od_forecasted_value = fields.Float('Forecasted Value')
    
    def od_view_costing_sheet(self,cr,uid,ids,context=None):
        ctx ={'default_lead_id':ids[0]}
        data = self.browse(cr,uid,ids)
        partner_id = data.partner_id and data.partner_id.id
        print "partner id>>>>>>>>>>>>>>>>>>>>>>>>>>>>",partner_id
        if partner_id:
            ctx['default_od_customer_id'] = partner_id
        sale_acc_mgr = data.user_id and data.user_id.id
        if sale_acc_mgr:
            ctx['default_sales_acc_manager'] = sale_acc_mgr
        bdm = data.od_bdm_user_id and data.od_bdm_user_id.id
        if bdm:
            ctx['default_business_development'] = bdm
        presale = data.od_responsible_id and data.od_responsible_id.id
        if presale:
            ctx['default_pre_sales_engineer'] = presale

        res = {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'od.cost.sheet',
            'domain': [('lead_id', '=',ids[0])],
            'context':ctx
        }
        return res
    def _od_costsheet_count(self, cr, uid, ids, field_name, arg, context=None):
        res ={}
        for obj in self.browse(cr, uid, ids, context):
            sheet_ids = self.pool.get('od.cost.sheet').search(cr, uid, [('lead_id', '=', obj.id)])
            if sheet_ids:
                res[obj.id] = len(sheet_ids)
        return res
    def create(self, cr, uid, vals, context=None):
        vals['od_number'] = self.pool.get('ir.sequence').get(cr, uid, 'crm.lead') or '/'
        return super(crm_lead, self).create(cr, uid, vals, context=context)

    def _get_act_window_dict(self, cr, uid, ids, name, context=None):
        print "haiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
        context['default_lead_id'] = context.get('active_id')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.xmlid_to_res_id(cr, uid, name, raise_if_not_found=True)

        result = act_obj.read(cr, uid, [result], context=context)[0]
        print "result >>>>>>>>>>>>>>>>",result
        result['domain'] = [('lead_id','=',ids[0])]

        return result
    
