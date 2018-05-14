# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from pprint import pprint
from datetime import datetime,timedelta,date as dt
from od_default_milestone import od_project_vals,od_om_vals,od_amc_vals
from openerp.exceptions import Warning
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
class account_invoice(models.Model):
    _inherit = 'account.invoice'
    cust_date = fields.Date(string="Customer Accepted Date")
    state = fields.Selection([('draft','Draft'),('proforma','Pro-forma'),('proforma2','Pro-forma'),('open','Open'),('accept','Accepted By Customer'),('paid','Paid'),('cancel','Cancelled'),('asset_done','Asset Done'),('manual','Manually Settled')],string="Invoice Status")
    @api.multi
    def od_accept(self):
        dt_today = str(dt.today())
        self.cust_date  = dt_today
        self.state = 'accept'

class account_move_line(models.Model):
    _inherit = "account.move.line"
    od_state = fields.Selection([('draft','Unposted'),('posted','Posted')],string="Parent Status",related="move_id.state")

class account_analytic_account(models.Model):
    _inherit = "account.analytic.account"
    DOMAIN = [('credit','Credit'),('sup','Supply'),('imp','Implementation'),('sup_imp','Supply & Implementation'),('amc','AMC'),('o_m','O&M'),('poc','(POC,Presales)'), ('comp_gen','Company General -(Training,Labs,Trips,etc.)')]
    od_type_of_project = fields.Selection(DOMAIN,string="Type Of Project")
    use_timesheets = fields.Boolean(string="Timesheets",readonly=True)
    use_tasks = fields.Boolean(string="Tasks",readonly=True)
    use_issues = fields.Boolean(string="Issues",readonly=True)
    
    od_project_invoice_schedule_line  = fields.One2many('od.project.invoice.schedule','analytic_id',string="Project Invoice Schedule")
    od_amc_invoice_schedule_line  = fields.One2many('od.amc.invoice.schedule','analytic_id',string="AMC Invoice Schedule")
    od_om_invoice_schedule_line  = fields.One2many('od.om.invoice.schedule','analytic_id',string="Operation Invoice Schedule")
    
    
    
    
    def get_product_id_from_param(self,product_param):
        parameter_obj = self.env['ir.config_parameter']
        key =[('key', '=', product_param)]
        product_param_obj = parameter_obj.search(key)
        if not product_param_obj:
            raise Warning(_('Settings Warning!'),_('NoParameter Not defined\nconfig it in System Parameters with %s'%product_param))
        product_id = product_param_obj.od_model_id and product_param_obj.od_model_id.id or False
        return product_id
    
    
    
    
    
    def get_projet_id(self):
        analytic_account_id = self.id 
        project =self.env['project.project'].search([('analytic_account_id','=',analytic_account_id)],limit=1)
        
        return project
    
    
    def create_milestone_tasks(self,task_vals,date_start,date_end):
        task_pool = self.env['project.task']
        project = self.get_projet_id()
        project_id = project.id
        user_id = project.user_id and project.user_id.id
        partner_ids = [(6,0,[user_id])],
        for val in task_vals:
            val.update({
            'project_id':project_id,
            'user_id':user_id,
            'partner_ids':partner_ids,
            'date_start':date_start,
            'date_end':date_end,
            'no_delete':True
            })
            task = task_pool.create(val)
        return True
    
    
    def create_crm_helpdesk(self):
        
        if len(self.preventive_maint_line) == 0:
            raise Warning("At Lease One Preventive Maintenance Schedule Needed to Activate AMC")
        help_desk = self.env['crm.helpdesk']
        project = self.get_projet_id()
        project_id = project.id
        user_id = self.od_amc_owner_id and self.od_amc_owner_id.id
        od_organization_id = self.partner_id and self.partner_id.id
        categ_id =17
        for line in self.preventive_maint_line:
            if not line.help_desk_id:
                vals = {
                    'od_sch_id':line.id,
                    'od_project_id':project_id,
                    'user_id':user_id,
                    'name':line.name,
                    'od_organization_id':od_organization_id,
                    'date_deadline':line.date,
                    'categ_id':categ_id,
                    'od_prev_create':True,
                    }
                hp_id =help_desk.create(vals)
                line['help_desk_id'] = hp_id.id
        
    
    def update_bools(self):
        self.write({'use_timesheets':True,'use_tasks':True,'use_issues':True})
    
    @api.multi
    def btn_activate_project(self):
        self.update_bools()
        task_vals = od_project_vals()
        date_start = self.od_project_start 
        date_end = self.od_project_end
        self.create_milestone_tasks(task_vals, date_start, date_end)
        self.od_project_status = 'active'
    
    @api.multi
    def btn_activate_amc(self):
        self.update_bools()
        task_vals = od_amc_vals()
        date_start = self.od_amc_start 
        date_end = self.od_amc_end
        self.create_milestone_tasks(task_vals, date_start, date_end)
        self.create_crm_helpdesk()
        self.od_amc_status = 'active'
        
    @api.multi
    def btn_activate_om(self):
        self.update_bools()
        task_vals = od_om_vals()
        date_start = self.od_om_start
        date_end = self.od_om_end
        self.create_milestone_tasks(task_vals, date_start, date_end)
        self.od_om_status = 'active'
        
    #closing
    
    @api.multi
    def btn_close_project(self):
        #need to update to acutal cost from jv
        today = str(dt.today())
        closing_date = today 
        self.od_project_closing = today
        
        self.od_project_status = 'close'
    
    
    @api.multi
    def btn_close_amc(self):
        #need to update to acutal cost from jv
        
        today = str(dt.today())
        closing_date = today 
        
        if self.od_project_status == 'active':
            raise Warning("Please Close the Project First")
        self.od_amc_closing = closing_date
        self.od_amc_status = 'close'
    
    @api.multi
    def btn_close_om(self):
        #need to update to acutal cost from jv
        
        today = str(dt.today())
        closing_date = today 
        
        if not closing_date:
            raise Warning("Please Fill the Closing Date")
        self.od_om_closing = closing_date
        self.od_om_status = 'close'
    
    
    
    
    def cron_od_contract_expiry(self, cr, uid,context=None):
        context = dict(context or {})
        remind = []

        
        def get_sender_addr(partner_id):
            email = ''
            partner_obj = self.pool.get('res.partner')
            partner_ids = partner_obj.search(cr,uid,[('parent_id','=',partner_id)],limit=1)
            if partner_ids:
                partner = partner_obj.browse(cr,uid,partner_ids)
                email = partner.email
            return email


        def fill_remind( domain):
            base_domain = []
            base_domain.extend(domain)
            analytic_ids = self.search(cr, uid, base_domain, context=context)
            for analytic in self.browse(cr,uid,analytic_ids,context=context):
                today = datetime.now().date()
                end_date = analytic.date
                if end_date:
                    partner_id = analytic.partner_id and analytic.partner_id.id
                    to_mail = get_sender_addr(partner_id)
                    days_diff = (today - datetime.strptime(end_date, '%Y-%m-%d')).days + 1
                    if days_diff < 7:
                        val = {'name':analytic.name,'code':analytic.code,'end_date':end_date,'to_mail':to_mail}
                        remind.append(val)

        for company_id in [1,6]:
            remind = []
            fill_remind([('state','not in',('close','cancelled')),('company_id','=',company_id)])
            template = 'od_contract_cron_email_template'
            if company_id == 6:
                template = template + '_saudi'
            template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'orchid_beta_project', template)[1]
            for val in remind:
                context["data"] = val
                if val:
                    self.pool.get('email.template').send_mail(cr, uid, template_id, uid, force_send=True, context=context)

        return True




    @api.one
    def od_get_timesheet_units(self):

        timesheet = self.env['hr.analytic.timesheet']
        analytic_id = self.id
        domain = [('account_id','=',analytic_id)]
        timesheet_obj = timesheet.search(domain)
        timesheet_units = sum([tm.unit_amount for tm in timesheet_obj])
        self.od_timesheet_units = timesheet_units
    def od_get_project(self):
        analytic_id = self.id
        project = self.env['project.project']
        domain = [('analytic_account_id','=',analytic_id)]
        project_obj = project.search(domain,limit=1)
        return project_obj
    @api.multi
    def set_close(self):
        project_obj = self.od_get_project()
        project_obj.write({'state':'close'})
        if self.od_project_status == 'active':
            self.btn_close_project()
        if self.od_amc_status == 'active':
            self.btn_close_amc()
        return super(account_analytic_account,self).set_close()

    @api.multi
    def set_open(self):
        project_obj = self.od_get_project()
        project_obj.write({'state':'open'})
        return super(account_analytic_account,self).set_open()

    @api.multi
    def set_cancel(self):
        project_obj = self.od_get_project()
        project_obj.write({'state':'cancelled'})
        self.write({'od_project_status':'cancel','od_amc_status':'cancel'})
        return super(account_analytic_account,self).set_cancel()

    @api.multi
    def set_pending(self):
        project_obj = self.od_get_project()
        project_obj.write({'state':'pending'})
        return super(account_analytic_account,self).set_pending()


    def od_update(self,values,data,key):
        if values.get(data,False):
            write_val = values.get(data)
            project_ob = self.od_get_project()
            project_ob.write({key:write_val})
    def od_update_vals(self,values):
        self.od_update(values,'od_owner_id','user_id')
        self.od_update(values,'quantity_max','od_quantity_max')
        self.od_update(values,'od_type_of_project','od_type_of_project')
    @api.multi
    def write(self, values):
        self.od_update_vals(values)
        return super(account_analytic_account, self).write(values)

    @api.one
    def od_get_sales_order_count(self):
        sale_order = self.env['sale.order']
        analytic_id = self.id
        domain =[('project_id','=',analytic_id)]
        count =len(sale_order.search(domain))
        self.od_sale_count = count

    @api.one
    @api.depends('od_cost_sheet_id')
    def od_get_po_status(self):
        if self.od_cost_sheet_id:
            self.od_po_status = self.od_cost_sheet_id.po_status


    @api.one
    def od_get_total_sale_value(self):
        sale_order = self.env['sale.order']
        analytic_id = self.id
        domain =[('project_id','=',analytic_id),('state','!=','cancel')]
        sales = sale_order.search(domain,limit=1)
#         total = sum([sal.amount_total for sal in sales])
        original_price = 0.0
        original_cost = 0.0
        original_profit =0.0
        original_profit_perc = 0.0
        amended_profit_perc = 0.0
        amended_price = 0.0
        amended_cost = 0.0
        planned_timesheet_cost = 0.0
#         for sale in sales:
#             for line in sale.order_line:
#                 if line.product_id.id in (211961,208829,208831):
#                     planned_timesheet_cost += line.od_original_line_cost
#                 original_price += line.od_original_line_price
#                 original_cost += line.od_original_line_cost
#                 amended_price += line.price_subtotal
#                 amended_cost += line.od_amended_line_cost
#         original_profit = original_price - original_cost
        
        
        if sales:
            original_price = sales.od_original_total_price
            original_cost = sales.od_original_total_cost
            
            amended_price = sales.od_amd_total_price
            amended_cost = sales.od_amd_total_cost
        original_profit = original_price - original_cost
        if original_price:
            original_profit_perc = (original_profit/original_price) *100
        
        amended_profit = amended_price - amended_cost
        if amended_price:
            amended_profit_perc = (amended_profit/amended_price) * 100
        self.od_original_sale_price = original_price
        self.od_original_sale_cost = original_cost
        self.od_original_sale_profit = original_profit
        self.od_original_sale_profit_perc = original_profit_perc
        self.od_amended_sale_price = amended_price
        self.od_amended_sale_cost = amended_cost
        self.od_amended_profit = amended_profit
        self.od_amended_profit_perc = amended_profit_perc
        self.od_planned_timesheet_cost = planned_timesheet_cost
    

    @api.one
    def od_get_total_purchase(self):
        purchase_order_line = self.env['purchase.order.line']
        analytic_id = self.id
        domain = [('account_analytic_id','=',analytic_id)]
        lines = purchase_order_line.search(domain)
        if lines:
            amount = sum([line.price_subtotal for line in lines])
            self.od_amnt_purchased = amount
            self.od_amnt_purchased2 = amount
#     @api.multi
#     def od_btn_open_invoice_lines(self):
#         analytic_id = self.id
#         inv_li_pool = self.env['account.invoice.line']
#         domain = [('account_analytic_id','=',analytic_id)]
#         raw_inv_ids = inv_li_pool.search(domain)
#         inv_li_ids = [line.id for line in raw_inv_ids if line.invoice_id.state not in ('draft','cancel')]
#         dom = [('id','in',inv_li_ids)]
#         return {
#             'domain':dom,
#             'view_type': 'form',
#             'view_mode': 'tree,form',
#             'res_model': 'account.invoice.line',
#             'type': 'ir.actions.act_window',
#         }
        
    
    
    
    @api.one
    def od_get_total_invoice(self):
        analytic_id = self.id
        invoice_pool = self.env['account.invoice']
        domain = [('od_analytic_account','=',analytic_id),('type','=','out_invoice'),('state','not in',('draft','cancel'))]
        inv_ids = invoice_pool.search(domain)
        amount_total = sum([inv.amount_total for inv in inv_ids])
        self.od_amnt_invoiced = amount_total
        self.od_amnt_invoiced2= amount_total
    
    @api.multi
    def od_btn_open_customer_invoice(self):
        analytic_id = self.id
        invoice_pool = self.env['account.invoice']
        domain = [('od_analytic_account','=',analytic_id),('type','=','out_invoice')]
        inv_ids = invoice_pool.search(domain)
        inv_li_ids = [inv.id for inv in inv_ids]
        dom = [('id','in',inv_li_ids)]
        
        model_data = self.env['ir.model.data']
        tree_view = model_data.get_object_reference('account', 'invoice_tree')
        form_view = model_data.get_object_reference('account', 'invoice_form')

        
        return {
            'domain':dom,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'views': [(tree_view and tree_view[1] or False, 'tree'),(form_view and form_view[1] or False, 'form'), ],
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def od_btn_open_purchase_lines(self):
        analytic_id = self.id
        domain = [('account_analytic_id','=',analytic_id)]
        return {
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order.line',
            'type': 'ir.actions.act_window',
        }

    def od_get_do(self):
        analytic_id = self.id
        domain = [('od_analytic_id','=',analytic_id)]
        picking_obj = self.env['stock.picking']
        pickings = picking_obj.search(domain)
        return pickings


    @api.multi
    def od_btn_open_delivery_orders(self):
        pickings = self.od_get_do()
        picking_ids = [pick.id for pick in pickings]
        dom = [('id','in',picking_ids)]
        return {
            'domain':dom,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def od_btn_open_sales_orders(self):
        sales_order = self.env['sale.order']
        analytic_id = self.id
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
    @api.multi
    def od_btn_open_lots(self):
        model_data = self.env['ir.model.data']
        pickings = self.od_get_do()
        picking_ids = [pick.id for pick in pickings]
        stock_pack_op_obj = self.env['stock.pack.operation']
        domain = [('picking_id','in',picking_ids)]
        pack_ops = stock_pack_op_obj.search(domain)
        pack_op_ids = [op.id for op in pack_ops]
        dom = [('id','in',pack_op_ids)]
        search_view_id = model_data.get_object_reference('orchid_beta_project', 'beta_project_stock_pakc_op_search_view')

        return {
            'name': _('Beta Lot Serial View'),
            'domain':dom,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.pack.operation',
            'type': 'ir.actions.act_window',

        }
    def od_action_schedule_meeting(self, cr, uid, ids, context=None):
        """
        Open meeting's calendar view to schedule meeting on current opportunity.
        :return dict: dictionary value for created Meeting view
        """
        analytic = self.browse(cr, uid, ids[0], context)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'calendar', 'action_calendar_event', context)
        partner_ids = [self.pool['res.users'].browse(cr, uid, uid, context=context).partner_id.id]
        if analytic.partner_id:
            partner_ids.append(analytic.partner_id.id)
        res['context'] = {
            'search_default_od_analytic_account_id': analytic.id,
            'default_od_analytic_account_id':analytic.id,
            'default_partner_id': analytic.partner_id and analytic.partner_id.id or False,
            'default_partner_ids': partner_ids,
            'default_name': analytic.name,
        }
        ctx = {
            'search_default_od_analytic_account_id': analytic.id,
            'default_od_analytic_account_id':analytic.id,
            'default_partner_id': analytic.partner_id and analytic.partner_id.id or False,
            'default_partner_ids': partner_ids,
            'default_name': analytic.name,
        }
        domain = [('od_analytic_account_id','=',analytic.id)]
        return {
            'domain':domain,
            'context':context,
            'view_type': 'form',
            'view_mode': 'tree,form,calendar',
            'res_model': 'calendar.event',
            'type': 'ir.actions.act_window',
        }
    @api.one
    def _od_meeting_count(self):
        Event = self.env['calendar.event']
        analytic_id = self.id
        domain = [('od_analytic_account_id','=',analytic_id)]
        meeting_count =0
        meeting_count = len(Event.search(domain))

        print "meet count",meeting_count
        self.od_meeting_count = meeting_count

    def od_open_timesheets(self, cr, uid, ids, context=None):
        """ open Timesheets view """
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        analytic_account_id = self.browse(cr, uid, ids[0], context)
        view_context = {
            'search_default_account_id': [analytic_account_id.id],
            'default_account_id': analytic_account_id.id,
        }
        res = mod_obj.get_object_reference(cr, uid, 'hr_timesheet', 'act_hr_timesheet_line_evry1_all_form')
        id = res and res[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        result['name'] = _('Timesheets')
        result['context'] = view_context

        return result
    @api.one
    def od_get_timesheet_amount(self):
        timesheet = self.env['hr.analytic.timesheet']
        analytic_id = self.id
        domain = [('account_id','=',analytic_id)]
        timesheet_obj = timesheet.search(domain)
        amount = sum([tm.normal_amount for tm in timesheet_obj])
        self.od_timesheet_amount = amount
        self.od_timesheet_amount2 = amount
    @api.multi
    def od_open_hr_expense_claim(self):
        hr_exp_line = self.env['hr.expense.line']
        analytic_id = self.id
        domain = [('analytic_account','=',analytic_id),('od_state','not in',('draft','cancelled','confirm','second_approval'))]
        return {
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense.line',
            'type': 'ir.actions.act_window',
        }
    @api.one
    def od_get_hr_exp_claim_amount(self):
        hr_exp_line = self.env['hr.expense.line']
        analytic_id = self.id
        domain = [('analytic_account','=',analytic_id),('od_state','not in',('draft','cancelled','confirm','second_approval'))]
        hr_exp_obj =hr_exp_line.search(domain)
        amount  = sum([hr.total_amount for hr in hr_exp_obj])
        self.od_hr_claim_amount = amount
    @api.multi
    def od_open_hr_expense_claim_draft(self):
        hr_exp_line = self.env['hr.expense.line']
        analytic_id = self.id
        domain = [('analytic_account','=',analytic_id),('od_state','in',('draft','cancelled','confirm','second_approval'))]
        return {
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense.line',
            'type': 'ir.actions.act_window',
        }
    @api.one
    def od_get_hr_exp_claim_amount_draft(self):
        hr_exp_line = self.env['hr.expense.line']
        analytic_id = self.id
        domain = [('analytic_account','=',analytic_id),('od_state','in',('draft','cancelled','confirm','second_approval'))]
        hr_exp_obj =hr_exp_line.search(domain)
        amount  = sum([hr.total_amount for hr in hr_exp_obj])
        self.od_hr_claim_amount_draft = amount

    @api.multi
    def od_btn_open_account_move_lines(self):
        analytic_id = self.id
        domain = [('analytic_account_id','=',analytic_id),('od_state','=','posted')]
        return {
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
        }
    @api.one
    def od_get_analytic_journal_amount(self):
        account_move_line = self.env['account.move.line']
        analytic_id = self.id
        exclude_journal_ids = self.get_exclude_journal_ids()
        domain = [('analytic_account_id','=',analytic_id),('journal_id','not in',exclude_journal_ids),('od_state','=','posted')]
        if self.state == 'close':
            cost_of_account_ids = self.get_cost_of_sale_account()
            domain = [('analytic_account_id','=',analytic_id),('account_id','in',cost_of_account_ids),('od_state','=','posted')]
        journal_lines = account_move_line.search(domain)
        amount = sum([mvl.debit for mvl in journal_lines])
        self.od_journal_amount = amount

    @api.multi
    def od_btn_open_account_move_lines_draft(self):
        analytic_id = self.id
        domain = [('analytic_account_id','=',analytic_id),('od_state','!=','posted')]
        return {
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
        }
    @api.one
    def od_get_analytic_journal_amount_draft(self):
        account_move_line = self.env['account.move.line']
        analytic_id = self.id
        exclude_journal_ids = self.get_exclude_journal_ids()
        domain = [('analytic_account_id','=',analytic_id),('journal_id','not in',exclude_journal_ids),('od_state','!=','posted')]
        journal_lines = account_move_line.search(domain)
        amount = sum([mvl.debit for mvl in journal_lines])
        self.od_journal_amount_draft = amount

    @api.one
    @api.depends('od_amended_sale_cost','od_original_sale_cost')
    def _od_get_cost_control_api(self):
        if self.od_amended_sale_cost > self.od_original_sale_cost :
            self.od_cost_control_kpi = 0
        else:
            self.od_cost_control_kpi = 100

    @api.one
    @api.depends('od_amended_profit_perc','od_original_sale_profit_perc')
    def _od_get_scope_control_kpi(self):
        if self.od_original_sale_profit_perc:
            check_val = self.od_amended_profit_perc / self.od_original_sale_profit_perc
            if check_val < 1:
                self.od_scope_control_kpi = 0
            else:
                self.od_scope_control_kpi = 100

    @api.one
    @api.depends('od_planned_timesheet_cost','od_timesheet_amount2')
    def _get_manpower_cost_control(self):
        if self.od_planned_timesheet_cost:
            if self.od_timesheet_amount2/self.od_planned_timesheet_cost <1:
                self.od_manpower_kpi = 100
            else:
                self.od_manpower_kpi = 0

#     @api.one
#     @api.depends('date')
#     def _get_original_date(self):
#         print "original date>>>>>>>>>>>>>>>",self.od_original_closing_date
#         if not self.od_date_set and self.date:
#             self.od_original_closing_date = self.date
#             self.od_date_set = True
    # od_original_closing_date = fields.Date(string="Original Closing Date",compute="_get_original_date",store=True)
    
    
    def get_value_from_param(self,param):
        parameter_obj = self.env['ir.config_parameter']
        key =[('key', '=', param)]
        param_obj = parameter_obj.search(key)
        if not param_obj:
            raise Warning(_('Settings Warning!'),_('NoParameter Not defined\nconfig it in System Parameters with %s'%param))
        result = param_obj.value
        return result
    def get_exclude_journal_ids(self):
        company_id =self.company_id and self.company_id.id 
        exclude_param ='exclude_journals'
        if company_id ==6:
            exclude_param = exclude_param +'_ksa'
        vals = self.get_value_from_param(exclude_param)
        vals = vals.split(',')
        result = [int(val) for val in vals]
        print "valssssssssssssssssssssss",vals,type(vals),result
        return result
    
    
    def get_cost_of_sale_account(self):
        company_id = self.company_id and self.company_id.id 
        account_ids = []
        if company_id ==6:
            account_ids = [5417]
        if company_id ==1:
            account_ids =[3488,3489]
        return account_ids
    @api.one
    def _get_cost_from_jv(self):
        analytic_id = self.id
        move_line_pool = self.env['account.move.line']
        exclude_journal_ids = self.get_exclude_journal_ids()
        domain = [('analytic_account_id','=',analytic_id),('journal_id','not in',exclude_journal_ids)]
        move_line_ids = move_line_pool.search(domain)
        actual_cost = sum([mvl.debit for mvl in move_line_ids if mvl.od_state =='posted'])
        
            
        project_cost =0.0
        amc_cost =0.0
        if self.od_project_closing:
            closing_date = self.od_project_closing 
            project_cost = sum([mvl.debit for mvl in move_line_ids if mvl.date <= closing_date and mvl.od_state =='posted'])
        if self.od_amc_closing:
            if self.od_project_closing:
                closing_date = self.od_project_closing 
                amc_cost = sum([mvl.debit for mvl in move_line_ids if mvl.date > closing_date and mvl.od_state =='posted'])
            else:
                amc_cost = sum([mvl.debit for mvl in move_line_ids if mvl.od_state =='posted'])
        
        if self.state == 'close':
            cost_of_sale_account_ids = self.get_cost_of_sale_account()
            print "cost of sale account ids>>>>>>>>>>>>>>",cost_of_sale_account_ids
            domain = [('analytic_account_id','=',analytic_id),('account_id','in',cost_of_sale_account_ids)]
            move_line_ids = move_line_pool.search(domain)
            actual_cost = sum([mvl.debit for mvl in move_line_ids if mvl.od_state =='posted'])
            project_cost = actual_cost
            print "actual cost in>>>>>>>>>>>>>>>>>>>>>from cost of cost salesssssssssssss",actual_cost
        
        self.od_actual_cost = actual_cost
        self.od_project_cost = project_cost 
        self.od_amc_cost = amc_cost
        
    
    @api.one 
    def _get_sale_value(self):
        analytic_id = self.id
        bmn_product_id = self.get_product_id_from_param('product_bmn')
        bmn_exp_product_id = self.get_product_id_from_param('product_bmn_extra_expense')
        omn_product_id = self.get_product_id_from_param('product_omn')
        omn_exp_product_id = self.get_product_id_from_param('product_omn_extra_expense')
        amc_products = [bmn_product_id,bmn_exp_product_id,omn_product_id,omn_exp_product_id]
        sale_order = self.env['sale.order'].search([('project_id','=',analytic_id),('state','!=','cancel')],limit=1)
        amc_sale =0.0
        project_sale =0.0
        actual_sale = 0.0
        project_original_sale =0.0
        amc_original_sale =0.0
        project_original_cost =0.0
        amc_original_cost=0.0
        project_amend_cost =0.0 
        amc_amend_cost =0.0
        project_amend_profit =0.0
        amc_amend_profit =0.0
       
        
        if sale_order:
            for line in sale_order.order_line:
                actual_sale += line.price_subtotal
                
                if line.product_id.id in amc_products:
                    amc_sale += line.price_subtotal
                    amc_original_sale += line.od_original_line_price
                    amc_original_cost += line.od_original_line_cost
                    amc_amend_cost += line.od_amended_line_cost
                else:
                    project_sale += line.price_subtotal
                    project_original_sale += line.od_original_line_price
                    project_original_cost += line.od_original_line_cost
                    project_amend_cost += line.od_amended_line_cost
        self.od_actual_sale = actual_sale
        self.od_amc_sale = amc_sale 
        self.od_project_sale = project_sale
        self.od_project_amend_sale = project_sale 
        self.od_amc_amend_sale = amc_sale
        self.od_project_amend_cost = project_amend_cost 
        self.od_amc_amend_cost = amc_amend_cost
        self.od_project_amend_profit = project_sale - project_amend_cost
        self.od_amc_amend_profit = amc_sale - amc_amend_cost    
        
        
        self.od_project_original_sale = project_original_sale 
        self.od_project_original_cost = project_original_cost 
        self.od_project_original_profit = project_original_sale -project_original_cost
        
        self.od_amc_original_sale = amc_original_sale 
        self.od_amc_original_cost = amc_original_cost 
        self.od_amc_original_profit = amc_original_sale - amc_original_cost
        
        
    
    
    @api.one 
    def _get_actual_profit(self):
        actual_profit = self.od_actual_sale - self.od_actual_cost
        actual_sale = self.od_actual_sale
        if actual_sale:
            actual_profit_percent = (actual_profit/float(actual_sale))*100.0
            self.od_actual_profit_percent = actual_profit_percent
        self.od_actual_profit = actual_profit
        self.od_project_profit = self.od_project_sale - self.od_project_cost 
        self.od_amc_profit = self.od_amc_sale - self.od_amc_cost 
    
    
    for i in range(1,6):
    ...:     for b in range(1,5):
    ...:         
    ...:         
    ...:         
    ...:         
    ...:         
    ...:         l1.append(('y'+str(i) +'-' +'q'+str(b),'AMC'+' '+'Y'+str(i) +'-
    ...: ' +'Q'+str(b)))
    
    
    def get_amc_yrs(self):
        res =[]
        for i in range(1,6):
            for b in range(1,5):
                res.append(('y'+str(i) +'-' +'q'+str(b),'AMC'+' '+'Y'+str(i) +'-' +'Q'+str(b)))
        return res 
    def get_type_list(self):
        amc_list = self.get_amc_yrs()
        stat_list = [('mat','MAT Supply Only'),('imp','IMP Service Only'),('project','Project (MAT & IMP)'),('trn','TRN'),('credit','Credit')]
        final_list  =  stat_list + amc_list
        return final_list
    
    od_actual_cost = fields.Float(string="Actual Cost",compute="_get_cost_from_jv")
    od_actual_sale = fields.Float(string="Actual Sale",compute="_get_sale_value")
    od_actual_profit = fields.Float(string="Actual Profit",compute="_get_actual_profit")
    od_actual_profit_percent = fields.Float(string="Actual Profit",compute="_get_actual_profit")
    
    od_project_type = fields.Selection(get_type_list,string="Project Type")
    od_project_start = fields.Date(string="Project Start")
    od_project_end = fields.Date(string="Project End")
    od_project_status = fields.Selection([('active','Active'),('inactive','Inactive'),('close','Closed'),('cancel','Cancelled')],string="Project Status",default='inactive',copy=False)
    od_project_owner_id = fields.Many2one('res.users',string="Project Owner")
    od_project_closing = fields.Date(string="Project Closing Date",copy=False)
    od_project_cost = fields.Float(string="Project Cost",compute="_get_cost_from_jv")
    od_project_sale =  fields.Float(string="Project Sale",compute="_get_sale_value")
    od_project_amend_sale =  fields.Float(string="Project Sale Amend",compute="_get_sale_value")
    od_project_amend_cost =  fields.Float(string="Project Cost Amend",compute="_get_sale_value")
    od_project_amend_profit =  fields.Float(string="Project Profit Amend",compute="_get_sale_value")
    od_project_original_sale =  fields.Float(string="Project Sale Amend",compute="_get_sale_value")
    od_project_original_cost =  fields.Float(string="Project Sale Amend",compute="_get_sale_value")
    od_project_original_profit =  fields.Float(string="Project Sale Amend",compute="_get_sale_value")
    od_project_profit = fields.Float(string="Project Profit",compute="_get_actual_profit")
    
    od_amc_type = fields.Selection(get_type_list,string="AMC Type")
    od_amc_start = fields.Date(string="AMC Start")
    od_amc_end = fields.Date(string="AMC End")
    od_amc_status = fields.Selection([('active','Active'),('inactive','Inactive'),('close','Closed'),('cancel','Cancelled')],string="Project Status",default='inactive',copy=False)
    od_amc_owner_id = fields.Many2one('res.users',string="AMC Owner")
    od_amc_closing = fields.Date(string="AMC Closing Date",copy=False)
    od_amc_cost = fields.Float(string="AMC Cost",compute="_get_cost_from_jv")
    od_amc_sale =  fields.Float(string="AMC Sale",compute="_get_sale_value")
    od_amc_amend_sale =  fields.Float(string="Project Sale Amend",compute="_get_sale_value")
    od_amc_amend_cost =  fields.Float(string="Project Cost Amend",compute="_get_sale_value")
    od_amc_amend_profit =  fields.Float(string="Project Profit Amend",compute="_get_sale_value")
    od_amc_original_sale =  fields.Float(string="Project Sale Amend",compute="_get_sale_value")
    od_amc_original_cost =  fields.Float(string="Project Sale Amend",compute="_get_sale_value")
    od_amc_original_profit =  fields.Float(string="Project Sale Amend",compute="_get_sale_value")
    od_amc_profit = fields.Float(string="AMC Profit",compute="_get_actual_profit")
    
    od_om_start = fields.Date(string="O&M Start")
    od_om_end = fields.Date(string="O&M End")
    od_om_status = fields.Selection([('active','Active'),('inactive','Inactive'),('close','Closed'),('cancel','Cancelled')],string="O&M Status",default='inactive')
    od_om_owner_id = fields.Many2one('res.users',string="OM Owner")
    od_om_closing = fields.Date(string="O&M Closing Date",copy=False)
    od_om_cost = fields.Float(string="O&M Cost")
    od_om_sale =  fields.Float(string="O&M Sale")
    od_om_profit = fields.Float(string="O&M Profit")
    
    
    od_cost_control_kpi = fields.Float(string="Cost Control KPI",compute="_od_get_cost_control_api")
    od_scope_control_kpi = fields.Float(string="Scope Control KPI",compute="_od_get_scope_control_kpi")
    od_manpower_kpi = fields.Float(string="Manpower Cost Control KPI",compute="_get_manpower_cost_control")
    od_timesheet_units = fields.Float(string="Timesheet Units",compute="od_get_timesheet_units")
    od_profit_percent = fields.Float(string="Profit Percentage",compute="od_get_total_sale_value")
    od_original_sale_price = fields.Float(string="Original Sale Price",compute="od_get_total_sale_value")
    od_original_sale_cost = fields.Float(string="Original Sale Cost",compute="od_get_total_sale_value")
    od_original_sale_profit = fields.Float(string="Original Sale Profit",compute="od_get_total_sale_value")
    od_original_sale_profit_perc = fields.Float(string="Original Sale Profit Perc",compute="od_get_total_sale_value")
    od_amended_sale_price = fields.Float(string="Amended Sale Price",compute="od_get_total_sale_value")
    od_amended_sale_cost = fields.Float(string="Amended Sale Cost",compute="od_get_total_sale_value")
    od_amended_profit = fields.Float(string="Amended Sale Profit",compute="od_get_total_sale_value")
    od_amended_profit_perc = fields.Float(string="Amended Sale Profit Perc",compute="od_get_total_sale_value")

    od_planned_timesheet_cost = fields.Float(string="Planned Timesheet Cost",compute="od_get_total_sale_value")
    od_po_status = fields.Selection([('waiting_po','Waiting P.O'),('special_approval','Special Approval From GM'),('available','Available')],'Customer PO Status',compute="od_get_po_status")
    od_journal_amount_draft = fields.Float(string="Journal Amount Draft",compute="od_get_analytic_journal_amount_draft")
    od_journal_amount = fields.Float(string="Journal Amount",compute="od_get_analytic_journal_amount")
    od_hr_claim_amount = fields.Float(string="Hr Exp Claim Amount",compute="od_get_hr_exp_claim_amount")
    od_hr_claim_amount_draft = fields.Float(string="Hr Exp Claim Amount Draft",compute="od_get_hr_exp_claim_amount_draft")
    od_timesheet_amount = fields.Float(string="Timesheet Amount",compute="od_get_timesheet_amount")
    od_timesheet_amount2 = fields.Float(string="Timesheet Amount",compute="od_get_timesheet_amount")
    od_owner_id = fields.Many2one('res.users',string="Owner",required=False)
    od_sale_count = fields.Integer(string="Sale Count",compute="od_get_sales_order_count")
    od_meeting_count = fields.Integer(string="Meeting Count",compute="_od_meeting_count")
    od_amnt_invoiced = fields.Float(string="Customer Invoice Amount",compute="od_get_total_invoice")
    od_amnt_invoiced2 = fields.Float(string="Customer Invoice Amount",compute="od_get_total_invoice")
   
    
    
    
    @api.one
    def od_get_cust_refund(self):
        analytic_id = self.id
        invoice_pool = self.env['account.invoice']
        domain = [('od_analytic_account','=',analytic_id),('type','=','out_refund'),('state','not in',('draft','cancel'))]
        inv_ids = invoice_pool.search(domain)
        amount_total = sum([inv.amount_total for inv in inv_ids])
        self.od_cust_refund_amt = amount_total
       
    
    @api.multi
    def od_btn_open_customer_refund(self):
        analytic_id = self.id
        invoice_pool = self.env['account.invoice']
        domain = [('od_analytic_account','=',analytic_id),('type','=','out_refund')]
        inv_ids = invoice_pool.search(domain)
        inv_li_ids = [inv.id for inv in inv_ids]
        dom = [('id','in',inv_li_ids)]
        
        model_data = self.env['ir.model.data']
        tree_view = model_data.get_object_reference('account', 'invoice_tree')
        form_view = model_data.get_object_reference('account', 'invoice_form')
        
        return {
            'domain':dom,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'views': [ (tree_view and tree_view[1] or False, 'tree'),(form_view and form_view[1] or False, 'form'),],
            'type': 'ir.actions.act_window',
        }
    
    @api.one
    def od_get_sup_inv_amnt(self):
        analytic_id = self.id
        invoice_pool = self.env['account.invoice']
        domain = [('od_analytic_account','=',analytic_id),('type','=','in_invoice'),('state','not in',('draft','cancel'))]
        inv_ids = invoice_pool.search(domain)
        amount_total = sum([inv.amount_total for inv in inv_ids])
        self.od_sup_inv_amt = amount_total
       
    
    @api.multi
    def od_btn_open_sup_invoice(self):
        analytic_id = self.id
        invoice_pool = self.env['account.invoice']
        domain = [('od_analytic_account','=',analytic_id),('type','=','in_invoice')]
        inv_ids = invoice_pool.search(domain)
        inv_li_ids = [inv.id for inv in inv_ids]
        dom = [('id','in',inv_li_ids)]
        return {
            'domain':dom,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
        }
    
    
    @api.one
    def od_get_sup_refund_amnt(self):
        analytic_id = self.id
        invoice_pool = self.env['account.invoice']
        domain = [('od_analytic_account','=',analytic_id),('type','=','in_refund'),('state','not in',('draft','cancel'))]
        inv_ids = invoice_pool.search(domain)
        amount_total = sum([inv.amount_total for inv in inv_ids])
        self.od_sup_refund_amt = amount_total
       
    
    @api.multi
    def od_btn_open_sup_refund(self):
        analytic_id = self.id
        invoice_pool = self.env['account.invoice']
        domain = [('od_analytic_account','=',analytic_id),('type','=','in_refund')]
        inv_ids = invoice_pool.search(domain)
        inv_li_ids = [inv.id for inv in inv_ids]
        dom = [('id','in',inv_li_ids)]
        return {
            'domain':dom,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
        }
    
    
    
    
    od_cust_refund_amt = fields.Float(string="Customer Refund Amount",compute="od_get_cust_refund")
    od_sup_inv_amt = fields.Float(string="Supplier Invoice Amount",compute="od_get_sup_inv_amnt")
    od_sup_refund_amt = fields.Float(string="Supplier Invoice Amount",compute="od_get_sup_refund_amnt")
    od_amnt_purchased = fields.Float(string="Supplier Purchase Amount",compute="od_get_total_purchase")
    od_amnt_purchased2 = fields.Float(string="Supplier Purchase Amount",compute="od_get_total_purchase")
    
    
    def get_day_procss_score(self):
        res =0.0
        cost_sheet_id = self.od_cost_sheet_id
        if cost_sheet_id:
            owner_kpi = cost_sheet_id.owner_kpi 
            if owner_kpi == 'ok':
                res =100.0
        return res
    
    
    def get_invoice_amounts(self):
    
        invoice_ids = self.env['account.invoice'].search([('od_analytic_account','=',self.id),('state','in',('open','paid'))])
        inv_amount =0.0
        for inv in invoice_ids:
            inv_amount+=inv.amount_total
        return inv_amount
    
    def get_x_days(self,date_start,date_end):
        fromdate = datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT)
        todate = datetime.strptime(date_end, DEFAULT_SERVER_DATE_FORMAT)
        daygenerator = (fromdate + timedelta(x + 1) for x in xrange((todate - fromdate).days))
        days =sum(1 for day in daygenerator)
        days = days+1
        return days  
    
    
    def get_avg_score(self,score_board):
        avg_score =0.0
        if score_board:
            avg_score =sum(score_board)/float(len(score_board))
        return avg_score
    def get_invoice_schedule_score(self):
        result =0.0
        type = self.od_type_of_project
        planned_amount = 0.0
        today = str(dt.today())
        score_board =[]
        if type not in ('credit','amc','o_m'):
            for line in self.od_project_invoice_schedule_line:
                date =line.date 
                if date <= today:
                    invoice = line.invoice_id 
                    planned_amount = line.amount 
                    invoice_amount = line.invoice_amount 
                    if planned_amount <invoice_amount:
                        score =0.0
                        score_board.append(score)
                        continue
                    if invoice and invoice.state in ('open','paid','accept'):
                        cust_date = invoice.cust_date 
                        score = 0.0
                        if cust_date <= date:
                            score = 100.0
                        score_board.append(score)
        avg_score = self.get_avg_score(score_board)
        return avg_score
    def get_cost_control_score(self):
        result =0.0
        actual_profit = self.od_project_profit
        original_profit = self.od_project_original_profit 
        if original_profit:
            result = (actual_profit/original_profit) * 100 
        if original_profit <=0.0 and actual_profit >0.0:
            result =100.0
        return result
    
    
    
    def get_avg_score_board(self,score_board):
        result =0.0
        if score_board:
            result = sum(score_board)/float(len(score_board))
        return result
    def get_compliance_score(self):
        score_board =[]
        
        score = [x.score for x in self.od_comp_planning_line if x.add_score]
        score_board.extend(score)
        
        score = [x.score for x in self.od_comp_initiation_line if x.add_score]
        score_board.extend(score)
        
        score = [x.score for x in self.od_comp_excecution_line if x.add_score]
        score_board.extend(score)
        
        score = [x.score for x in self.od_comp_monitor_line if x.add_score]
        score_board.extend(score)    
        
        score = [x.score for x in self.od_comp_closing_line if x.add_score]
        score_board.extend(score)
        if self.od_type_of_project == 'amc':
            score_board =[]
            score = [x.score for x in self.od_comp_handover_line if x.add_score]
            score_board.extend(score)
            
            score = [x.score for x in self.od_comp_maint_line if x.add_score]
            score_board.extend(score)
        result = self.get_avg_score_board(score_board)
        return result
    
    def get_schedule_control_score(self):
        result =0.0
        project_planned_end = self.od_project_end 
        closed_date = self.od_project_closing 
        if closed_date <= project_planned_end:
            result =100.0
        return result
            
        
    
    
    @api.one
    def _kpi_score(self):
        
        day_process_score = .1 *self.get_day_procss_score()
        invoice_schedule_score =  .3 *self.get_invoice_schedule_score()
        cost_control_score = .2 * self.get_cost_control_score()
        compliance_score = .1 * self.get_compliance_score()
        schedule_control_score = .3 * self.get_schedule_control_score()
        
           
#         day_process_score = .1 *self.get_day_procss_score()
#         invoice_schedule_score =  .3 *self.get_invoice_schedule_score()
#         cost_control_score = .1 * self.get_cost_control_score()
#         compliance_score = .1 * self.get_compliance_score()
#         schedule_control_score = self.get_schedule_control_score()
        
        
        total_score = day_process_score + invoice_schedule_score + cost_control_score+ compliance_score + schedule_control_score
        self.day_process_score = day_process_score 
        self.invoice_schedule_score = invoice_schedule_score 
        self.cost_control_score = cost_control_score 
        self.compliance_score = compliance_score 
        self.schedule_control_score = schedule_control_score
        self.total_score = total_score
    day_process_score = fields.Float(string="Day Process Score",compute="_kpi_score")
    invoice_schedule_score = fields.Float(string="Invoice Schedule Score",compute="_kpi_score")
    cost_control_score = fields.Float(string="Cost Control Score",compute="_kpi_score")
    compliance_score = fields.Float(string="Compliance Score",compute="_kpi_score")
    total_score = fields.Float(string="Total Score",compute="_kpi_score")
    schedule_control_score = fields.Float(string="Compliance Score",compute="_kpi_score")
    
    
    
        

    
    
    def get_initiation_line(self):
        data = [
            (0,0,{'name':'Project Charter'}),
            (0,0,{'name':'Sales Handover'}),
            
            ]
        return data
    
    def get_planning_line(self):
        data = [
            (0,0,{'name':'High Level Design (HLD) & Its Approval'}),
            (0,0,{'name':'Project Scope Document & Its Approval'}),
            (0,0,{'name':'Low Level Design (LLD) & Its Approval'}),
            (0,0,{'name':'Project Plan & Its Approval'}),
            (0,0,{'name':'Migration Plans & Their Approvals'}),
            (0,0,{'name':'User Acceptance Test Document (UAT) & Its Approval'}),
            (0,0,{'name':'Technical Drawings'}),
            ]
        return data
    def get_execution_line(self):
        data = [
            (0,0,{'name':' Customer Invoices'}),
            (0,0,{'name':'Delivery Notes'}),
            (0,0,{'name':'Supplier Purchases'}),
            (0,0,{'name':'Correspondence'}),
           
            ]
        return data
    
    def get_monitor_line(self):
        data = [
            (0,0,{'name':'Change Management (Change Requests)'}),
            (0,0,{'name':'Project Logs (Issues & Risks)'}),
            (0,0,{'name':'Progress / Status Reports'}),
            (0,0,{'name':'Updated Project Plans'}),
           
            ]
        return data
    
    def get_closing_line(self):
        data = [
            (0,0,{'name':'Completion Certificates'}),
            (0,0,{'name':'Final Project Documentation'}),
            (0,0,{'name':'Serial Numbers'}),
            (0,0,{'name':'Backup Configuration'}),
            (0,0,{'name':'Lessons Learn'}),
            (0,0,{'name':'Handover to Service Desk (Signed SLA)'}),
           
            ]
        return data
    
    def get_handover_line(self):
        data = [
            (0,0,{'name':'Final Project Documentation'}),
            (0,0,{'name':'Serial Numbers'}),
            (0,0,{'name':'Backup Configuration'}),
            (0,0,{'name':'Signed SLA'}),
           
           
            ]
        return data
    
    def get_maint_line(self):
        data = [
            (0,0,{'name':'Reports (Preventive, RMA, etc.)'}),
            (0,0,{'name':'Issue Updates'}),
            ]
        return data
    start_project_comp = fields.Boolean(string="Start Project Compliance")
    start_amc_comp = fields.Boolean(string="Start AMC Compliance")
    od_comp_initiation_line  = fields.One2many('od.compliance.initiation','analytic_id',string="Detail Line",default=get_initiation_line)
    od_comp_planning_line  = fields.One2many('od.compliance.planning','analytic_id',string="Detail Line",default=get_planning_line)
    od_comp_excecution_line  = fields.One2many('od.compliance.execution','analytic_id',string="Detail Line",default=get_execution_line)
    od_comp_monitor_line  = fields.One2many('od.compliance.monitor','analytic_id',string="Detail Line",default=get_monitor_line)
    od_comp_closing_line  = fields.One2many('od.compliance.closing','analytic_id',string="Detail Line",default=get_closing_line)
    od_comp_handover_line  = fields.One2many('od.compliance.handover','analytic_id',string="Detail Line",default=get_handover_line)
    od_comp_maint_line  = fields.One2many('od.compliance.maint','analytic_id',string="Detail Line",default=get_maint_line)
    preventive_maint_line = fields.One2many('preventive.maint.schedule','analytic_id',string="Detail Line")
   
    

class od_compliance_initiation(models.Model):
    _name = "od.compliance.initiation"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    add_score = fields.Boolean(string="Add Score")
    score = fields.Float(string="Score")
class od_compliance_planning(models.Model):
    _name = "od.compliance.planning"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    score = fields.Float(string="Score")
    add_score = fields.Boolean(string="Add Score")
class od_compliance_execution(models.Model):
    _name = "od.compliance.execution"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    score = fields.Float(string="Score")
    add_score = fields.Boolean(string="Add Score")
class od_compliance_monitor(models.Model):
    _name = "od.compliance.monitor"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    score = fields.Float(string="Score")
    add_score = fields.Boolean(string="Add Score")
class od_compliance_closing(models.Model):
    _name = "od.compliance.closing"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    score = fields.Float(string="Score")
    add_score = fields.Boolean(string="Add Score")
class od_compliance_handover(models.Model):
    _name = "od.compliance.handover"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    score = fields.Float(string="Score")
    add_score = fields.Boolean(string="Add Score")
class od_compliance_maint(models.Model):
    _name = "od.compliance.maint"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    score = fields.Float(string="Score")
    add_score = fields.Boolean(string="Add Score")

class od_project_invoice_schedule(models.Model):
    _name = "od.project.invoice.schedule"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    date = fields.Date(string="Planned Date",required=True)
    invoice_id = fields.Many2one('account.invoice',string="Invoice")
    amount = fields.Float(string="Planned Amount",required=True)
    invoice_amount = fields.Float(string="Invoice Amount",related="invoice_id.amount_total",readonly=True,store=True)
    date_invoice = fields.Date(string="Invoice Date",related="invoice_id.date_invoice",readonly=True,store=True)
    invoice_status = fields.Selection([('draft','Draft'),('proforma','Pro-forma'),('proforma2','Pro-forma'),('open','Open'),('accept','Accepted By Customer'),('paid','Paid'),('cancel','Cancelled')],related="invoice_id.state",raeadonly=True,string="Invoice Status",store=True)
    cust_date = fields.Date(string="Customer Accepted Date",related="invoice_id.cust_date",readonly=True,store=True)
    def _prepare_invoice_line(self, cr, uid, line,analytic_id, fiscal_position=False, context=None):
        fpos_obj = self.pool.get('account.fiscal.position')
        res = line.product_id
        account_id = res.property_account_income.id
        if not account_id:
            account_id = res.categ_id.property_account_income_categ.id
        account_id = fpos_obj.map_account(cr, uid, fiscal_position, account_id)

        taxes = line.tax_id or False
        tax_id = fpos_obj.map_tax(cr, uid, fiscal_position, taxes, context=context)
        values = {
            'name': line.name,
            'account_id': account_id,
            'account_analytic_id': analytic_id ,
            'price_unit': line.price_unit or 0.0,
            'quantity': line.product_uom_qty,
            'uos_id': line.product_uom.id or False,
            'product_id': line.product_id.id or False,
            'invoice_line_tax_id': [(6, 0, tax_id)],
        }
        return values
    
    @api.multi 
    def create_invoice(self):
        analytic_id = self.analytic_id and self.analytic_id.id or False
        cr = self.env.cr
        uid = self.env.uid
        inv_line_vals =[]
        od_cost_sheet_id = self.analytic_id and self.analytic_id.od_cost_sheet_id and self.analytic_id.od_cost_sheet_id.id or False 
        od_branch_id  = self.analytic_id and self.analytic_id.od_branch_id and self.analytic_id.od_branch_id.id or False 
        od_cost_centre_id = self.analytic_id and self.analytic_id.od_cost_centre_id and self.analytic_id.od_cost_centre_id.id or False 
        od_division_id = self.analytic_id and self.analytic_id.od_division_id and self.analytic_id.od_division_id.id or False 
        if analytic_id and not self.invoice_id:
            so_id = self.env['sale.order'].search([('project_id','=',analytic_id),('state','!=','cancel')],limit=1)
            inv_vals =  self.pool.get('sale.order')._prepare_invoice(cr,uid,so_id,[])
            inv_vals['date_invoice'] =str(dt.today())
            inv_vals.update({
                'od_cost_sheet_id':od_cost_sheet_id,
                'od_branch_id':od_branch_id,
                'od_cost_centre_id':od_cost_centre_id,
                'od_division_id':od_division_id,
                'od_costing':False,
                'od_inter_inc_acc_id':so_id.od_order_type_id and so_id.od_order_type_id.income_acc_id and so_id.od_order_type_id.income_acc_id.id,
                'od_inter_exp_acc_id':so_id.od_order_type_id and so_id.od_order_type_id.expense_acc_id and so_id.od_order_type_id.expense_acc_id.id,
                })
            for line in so_id.order_line:
                vals = self._prepare_invoice_line(line,analytic_id) 
                print "valssssssssssss>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",vals
                inv_line_vals.append((0,0,vals))
            inv_vals['invoice_line'] = inv_line_vals
            inv =self.env['account.invoice'].create(inv_vals)
            inv.button_compute()
            self.invoice_id = inv.id
            model_data = self.env['ir.model.data']
            tree_view = model_data.get_object_reference('account', 'invoice_tree')
            form_view = model_data.get_object_reference('account', 'invoice_form')
            return {
                'res_id':inv.id,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'views': [(form_view and form_view[1] or False, 'form'),(tree_view and tree_view[1] or False, 'tree')], 
                'type': 'ir.actions.act_window',
            }
        return True

class od_amc_invoice_schedule(models.Model):
    _name = "od.amc.invoice.schedule"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    date = fields.Date(string="Planned Date",required=True)
    amount = fields.Float(string="Planned Amount",required=True)
    invoice_id = fields.Many2one('account.invoice',string="Invoice")
    invoice_amount = fields.Float(string="Invoice Amount",related="invoice_id.amount_total",readonly=True)
    date_invoice = fields.Date(string="Invoice Date",related="invoice_id.date_invoice",readonly=True)
    invoice_status = fields.Selection([('draft','Draft'),('proforma','Pro-forma'),('proforma2','Pro-forma'),('open','Open'),('accept','Accepted By Customer'),('paid','Paid'),('cancel','Cancelled')],related="invoice_id.state",raeadonly=True,string="Invoice Status")
    cust_date = fields.Date(string="Customer Accepted Date",related="invoice_id.cust_date",readonly=True)
    def _prepare_invoice_line(self, cr, uid, line,analytic_id, fiscal_position=False, context=None):
        fpos_obj = self.pool.get('account.fiscal.position')
        res = line.product_id
        account_id = res.property_account_income.id
        if not account_id:
            account_id = res.categ_id.property_account_income_categ.id
        account_id = fpos_obj.map_account(cr, uid, fiscal_position, account_id)

        taxes = line.tax_id or False
        tax_id = fpos_obj.map_tax(cr, uid, fiscal_position, taxes, context=context)
        values = {
            'name': line.name,
            'account_id': account_id,
            'account_analytic_id': analytic_id ,
            'price_unit': line.price_unit or 0.0,
            'quantity': line.product_uom_qty,
            'uos_id': line.product_uom.id or False,
            'product_id': line.product_id.id or False,
            'invoice_line_tax_id': [(6, 0, tax_id)],
        }
        return values
    
    @api.multi 
    def create_invoice(self):
        analytic_id = self.analytic_id and self.analytic_id.id or False
        cr = self.env.cr
        uid = self.env.uid
        inv_line_vals =[]
        od_cost_sheet_id = self.analytic_id and self.analytic_id.od_cost_sheet_id and self.analytic_id.od_cost_sheet_id.id or False 
        od_branch_id  = self.analytic_id and self.analytic_id.od_branch_id and self.analytic_id.od_branch_id.id or False 
        od_cost_centre_id = self.analytic_id and self.analytic_id.od_cost_centre_id and self.analytic_id.od_cost_centre_id.id or False 
        od_division_id = self.analytic_id and self.analytic_id.od_division_id and self.analytic_id.od_division_id.id or False 
        if analytic_id and not self.invoice_id:
            so_id = self.env['sale.order'].search([('project_id','=',analytic_id),('state','!=','cancel')],limit=1)
            inv_vals =  self.pool.get('sale.order')._prepare_invoice(cr,uid,so_id,[])
            inv_vals['date_invoice'] =str(dt.today())
            inv_vals.update({
                'od_cost_sheet_id':od_cost_sheet_id,
                'od_branch_id':od_branch_id,
                'od_cost_centre_id':od_cost_centre_id,
                'od_division_id':od_division_id,
                'od_costing':False,
                'od_inter_inc_acc_id':so_id.od_order_type_id and so_id.od_order_type_id.income_acc_id and so_id.od_order_type_id.income_acc_id.id,
                'od_inter_exp_acc_id':so_id.od_order_type_id and so_id.od_order_type_id.expense_acc_id and so_id.od_order_type_id.expense_acc_id.id,
                })
            for line in so_id.order_line:
                vals = self._prepare_invoice_line(line,analytic_id) 
                print "valssssssssssss>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",vals
                inv_line_vals.append((0,0,vals))
            inv_vals['invoice_line'] = inv_line_vals
            inv =self.env['account.invoice'].create(inv_vals)
            inv.button_compute()
            self.invoice_id = inv.id
            model_data = self.env['ir.model.data']
            tree_view = model_data.get_object_reference('account', 'invoice_tree')
            form_view = model_data.get_object_reference('account', 'invoice_form')
            return {
                'res_id':inv.id,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'views': [(form_view and form_view[1] or False, 'form'),(tree_view and tree_view[1] or False, 'tree')], 
                'type': 'ir.actions.act_window',
            }
        return True
class od_om_invoice_schedule(models.Model):
    _name = "od.om.invoice.schedule"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    date = fields.Date(string="Planned Date",required=True)
    amount = fields.Float(string="Amount",required=True)

class preventive_maint_schedule(models.Model):
    _name = "preventive.maint.schedule"
    analytic_id  = fields.Many2one('account.analytic.account',string="Analytic Account")
    name = fields.Char(string="Name",required=True)
    date = fields.Date(string="Date",required=True)
    help_desk_id = fields.Many2one('crm.helpdesk',string="Help Desk")
    
