# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import Warning

class ChangeType(models.Model):
    _name = 'change.type'
    name = fields.Char(string="Name")

class ImpactSale(models.Model):
    _name = 'impact.sale'
    name = fields.Char(string="Name")
class ImpactCost(models.Model):
    _name = 'impact.cost'
    name = fields.Char(string="Name")
class ImpactProfit(models.Model):
    _name = 'impact.profit'
    name = fields.Char(string="Name")

class ChangeManagement(models.Model):
    _name = 'change.management'
    
    notes = fields.Text(string="Notes")
    
    def get_current_user(self):
        return self._uid
    
    
    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].get('change.management') or '/'
        return super(ChangeManagement, self).create(vals)
    
    def od_send_mail(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        if self.company_id.id == 6:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference('orchid_cost_sheet', template)[1]
        print "template id>>>>>>>>>>>>>>>>>>>>>>>>>>",template_id
        cost_sheet_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,cost_sheet_id, force_send=True)
        return True
    
    
    @api.onchange('user_id')
    def onchange_user_id(self):
        hr = self.env['hr.employee']
        manager = False
        coach_id = False 
        branch_id = False
        if self.user_id:
            user_id = self.user_id.id
            users_list =hr.search([('user_id','=',user_id)])
            print "user list>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",users_list
            if users_list :
                manager = users_list.parent_id and users_list.parent_id.user_id and users_list.parent_id.user_id.id or False
                coach_id = users_list.coach_id and users_list.coach_id.user_id and users_list.coach_id.user_id.id or False
                branch_id = users_list.od_branch_id and users_list.od_branch_id.id  or False
        self.manager_id = manager
        self.first_approval_manager_id = coach_id
        self.branch_id = branch_id
    
    selection_list = [
            ('draft','Draft'),
            ('imported','Imported'),
            ('submit','Submitted'),
            ('first_approval','First Approval'),
            ('third_approval','Final Approval'),
            ('cancel','Cancel'),
            ('reject','Rejected')
            ]
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id,readonly=True)
    state = fields.Selection(selection_list,string="Status",default='draft')
    name = fields.Char(string="Reference",readonly=True)
    manager_id = fields.Many2one('res.users',string="Direct Manager")
    first_approval_manager_id = fields.Many2one('res.users',string="First Approval Manager")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    date = fields.Date(string="Requested Date",default=fields.Date.context_today)
    closing_date = fields.Date(string="Closing Date")
    so_id = fields.Many2one('sale.order',string="Sale Order")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet",readonly=False)
    project_id = fields.Many2one('account.analytic.account',string="Project",readonly=False)
    change_type_id = fields.Many2one('change.type',string="Change Type")
    change_method = fields.Selection([('allow_change','Allow Change'),('redist','Redistribute Analytic')],string="Change Method",required=True)
    change_line = fields.One2many('change.order.line','change_id',string="Change line")
    total_price = fields.Float(string='Total Price',compute="compute_values")
    total_cost = fields.Float(string='Total Cost',compute="compute_values")
    profit = fields.Float(string="Profit",compute="compute_values")
    profit_percent = fields.Float(string="Profit Percentage",compute="compute_values")
    new_total_price = fields.Float(string="New Total Price",compute="compute_values")
    new_total_cost = fields.Float(string="New Total Cost",compute="compute_values")
    new_profit = fields.Float(string="New Total Profit",compute="compute_values")
    new_profit_percent = fields.Float(string="New Profit Percentage",compute="compute_values")
    user_id = fields.Many2one('res.users',string="Requested By",default=get_current_user)
    first_approval_by =fields.Many2one('res.users',string="First Approval By")
    first_approval_date = fields.Date(string="First Approval Date")
    second_approval_by =fields.Many2one('res.users',string="Second Approval By")
    second_approval_date = fields.Date(string="Second Approval Date")
    third_approval_by =fields.Many2one('res.users',string="Third Approval By")
    third_approval_date = fields.Date(string="Third Approval Date")
    impact_sale_id = fields.Many2one('impact.sale',string="Impact On Sale")
    impact_cost_id = fields.Many2one('impact.cost',string="Impact On Cost")
    impact_profit_id = fields.Many2one('impact.profit',string="Impact On Profit")
    
    @api.one 
    def unlink(self):
        if self.state not in ('draft','cancel','reject'):
            raise Warning("Cannot Delete This record on this state")
        return super(ChangeManagement,self).unlink()

    @api.one
    @api.depends('change_line')
    def compute_values(self):
        total_price = 0.0
        total_cost = 0.0
        new_total_price = 0.0
        new_total_cost = 0.0
        profit_percent = 0.0
        new_profit_percent = 0.0
        for line in self.change_line:
            total_price += line.total_price
            total_cost += line.od_amended_line_cost
            if not line.remove_item:
                new_total_price += line.new_total_price
                new_total_cost += line.new_total_cost
        profit = total_price -total_cost
        new_total_profit =  new_total_price - new_total_cost
        if total_price:
            profit_percent = profit/total_price
            self.profit_percent = profit_percent *100
        if  new_total_price:
            new_profit_percent = new_total_profit/new_total_price
            self.new_profit_percent = new_profit_percent * 100
        self.total_price = total_price
        self.total_cost = total_cost
        self.profit = profit
        self.new_total_price = new_total_price
        self.new_total_cost = new_total_cost
        self.new_profit = new_total_profit
    @api.one
    def import_sale(self):
        sale_id = self.so_id
        if not sale_id:
            raise Warning("Please Choose Sale Order")
        line_vals = []
        for line in sale_id.order_line:
            vals ={
                   'product_id':line.product_id and line.product_id.id or False,
                   'od_manufacture_id':line.od_manufacture_id and line.od_manufacture_id or False,
                   'name':line.name,
                   'product_uom_qty':line.product_uom_qty,
                   'price_unit':line.price_unit,
                   'purchase_price':line.purchase_price,
                   'change_qty':line.product_uom_qty,
                   'change_price':line.price_unit,
                   'change_cost':line.purchase_price,
                   
                   }
            line_vals.append(vals)
        self.change_line.unlink()
        self.change_line = line_vals
        self.state ='imported'
    @api.one 
    def button_submit(self):
        
        cost_sheet_id = self.cost_sheet_id
        cost_sheet_state = self.cost_sheet_id.state
        if cost_sheet_state != 'done':
            raise Warning("Cost Sheet Not in Done State ,Pls Check the Costsheet")
        self.state = 'submit'
        
        self.od_send_mail('cm_submit_mail')
    
    @api.one 
    def button_first_approval(self):
        cost_sheet_id = self.cost_sheet_id
        cost_sheet_state = self.cost_sheet_id.state
        if cost_sheet_state != 'done':
            raise Warning("Cost Sheet Not in Done State ,Pls Check the Costsheet")
        self.first_approval_by = self._uid
        self.first_approval_date = fields.Date.context_today(self)
        self.state = 'first_approval'
        self.od_send_mail('cm_first_approval_mail')
    
    @api.one 
    def button_second_approval(self):
        cost_sheet_id = self.cost_sheet_id
        cost_sheet_state = self.cost_sheet_id.state
        if cost_sheet_state != 'done':
            raise Warning("Cost Sheet Not in Done State ,Pls Check the Costsheet")
        self.second_approval_by = self._uid
        self.second_approval_date = fields.Date.context_today(self)
        self.state = 'second_approval'
        self.od_send_mail('cm_second_approval_mail')
        
    @api.one 
    def button_third_approval(self):
        self.third_approval_by = self._uid
        self.third_approval_date = fields.Date.context_today(self)
        method= self.change_method
        cost_sheet_id = self.cost_sheet_id
        cost_sheet_state = self.cost_sheet_id.state
        if cost_sheet_state != 'done':
            raise Warning("Cost Sheet Not in Done State ,Pls Check the Costsheet")
        if method == 'allow_change':
            cost_sheet_id.btn_allow_change()
        elif method == 'redist':
            cost_sheet_id.btn_redistribute_analytic()
        self.state = 'third_approval'
        self.od_send_mail('cm_third_approval_mail')
    @api.one 
    def button_cancel(self):
        self.state= 'cancel'
        self.od_send_mail('cm_cancel_mail')
    
    @api.one 
    def button_reject(self):
        self.state= 'reject'
        self.od_send_mail('cm_reject_mail')
        
    
  
            
    
class ChangeOrderLine(models.Model):
    _name = "change.order.line"
    _inherit = "sale.order.line"
    change_id = fields.Many2one('change.management',string="Change")
    order_id = fields.Many2one('sale.order',required=False)
    total_price = fields.Float(string="Total Price",compute="_od_get_total_price")
    change_qty = fields.Float(string="Change Qty")
    change_price = fields.Float(string="Change Price")
    new_total_price = fields.Float(string="New Total Price",compute="_od_get_total_price")
    change_cost = fields.Float(string="Change Cost")
    new_total_cost = fields.Float(string="New Total Cost",compute="_od_get_total_price")
    remove_item = fields.Boolean(string="Remove Item")
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            desc = (self.product_id and self.product_id.description_sale) or (self.product_id and self.product_id.description) or (self.product_id and self.product_id.name)
            self.name = desc
            
    @api.one
    @api.depends('product_uom_qty','price_unit','change_qty','change_price','change_cost','remove_item')
    def _od_get_total_price(self):
        self.total_price = self.get_line_price(self.product_uom_qty,self.price_unit)
        if self.remove_item:
            self.new_total_price = 0.0
            self.new_total_cost = 0.0
        else:
            self.new_total_price = self.get_line_price(self.change_qty,self.change_price)
            self.new_total_cost = self.get_line_price(self.change_qty,self.change_cost)
        
