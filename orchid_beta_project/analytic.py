# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from pprint import pprint
from datetime import datetime
class account_move_line(models.Model):
    _inherit = "account.move.line"
    od_state = fields.Selection([('draft','Unposted'),('posted','Posted')],string="Parent Status",related="move_id.state")

class account_analytic_account(models.Model):
    _inherit = "account.analytic.account"
    DOMAIN = [('credit','Credit'),('sup','Supply'),('imp','Implementation'),('sup_imp','Supply & Implementation'),('amc','AMC'),('o_m','O&M')]
    od_type_of_project = fields.Selection(DOMAIN,string="Type Of Project")
   
    
    
    
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
        domain =[('project_id','=',analytic_id)]
        sales = sale_order.search(domain)
        total = sum([sal.amount_total for sal in sales])
        original_price = 0.0
        original_cost = 0.0
        original_profit_perc = 0.0
        amended_profit_perc = 0.0
        amended_price = 0.0
        amended_cost = 0.0
        planned_timesheet_cost = 0.0
        for sale in sales:
            for line in sale.order_line:
                if line.product_id.id in (211961,208829,208831):
                    planned_timesheet_cost += line.od_original_line_cost
                original_price += line.od_original_line_price
                original_cost += line.od_original_line_cost
                amended_price += line.price_subtotal
                amended_cost += line.od_amended_line_cost
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
    def od_get_total_invoice(self):
        invoice_line = self.env['account.invoice.line']
        analytic_id = self.id
        domain = [('account_analytic_id','=',analytic_id)]
        lines = invoice_line.search(domain)
        if lines:
            amount = sum([line.price_subtotal for line in lines if line.invoice_id.state not in ('draft','cancel')])
            self.od_amnt_invoiced = amount
            self.od_amnt_invoiced2= amount

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
    @api.multi
    def od_btn_open_invoice_lines(self):
        analytic_id = self.id
        inv_li_pool = self.env['account.invoice.line']
        domain = [('account_analytic_id','=',analytic_id)]
        raw_inv_ids = inv_li_pool.search(domain)
        inv_li_ids = [line.id for line in raw_inv_ids if line.invoice_id.state not in ('draft','cancel')]
        dom = [('id','in',inv_li_ids)]
        return {
            'domain':dom,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice.line',
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
        amount = sum([tm.amount for tm in timesheet_obj])
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
        domain = [('analytic_account_id','=',analytic_id),('od_state','=','posted')]
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
        domain = [('analytic_account_id','=',analytic_id),('od_state','!=','posted')]
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

    @api.one
    @api.depends('date')
    def _get_original_date(self):
        print "original date>>>>>>>>>>>>>>>",self.od_original_closing_date
        if not self.od_date_set and self.date:
            self.od_original_closing_date = self.date
            self.od_date_set = True
    # od_original_closing_date = fields.Date(string="Original Closing Date",compute="_get_original_date",store=True)
    
    od_project_start = fields.Date(string="Project Start")
    od_project_end = fields.Date(string="Project End")
    od_project_status = fields.Selection([('active','Active'),('inactive','Inactive')],string="Project Status",default='inactive')

    
    od_amc_start = fields.Date(string="AMC Start")
    od_amc_end = fields.Date(string="AMC End")
    od_amc_status = fields.Selection([('active','Active'),('inactive','Inactive')],string="Project Status",default='inactive')

    
    od_om_start = fields.Date(string="O&M Start")
    od_om_end = fields.Date(string="O&M End")
    od_om_status = fields.Selection([('active','Active'),('inactive','Inactive')],string="O&M Status",default='inactive')



    
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
    od_owner_id = fields.Many2one('res.users',string="Owner",required=True)
    od_sale_count = fields.Integer(string="Sale Count",compute="od_get_sales_order_count")
    od_meeting_count = fields.Integer(string="Meeting Count",compute="_od_meeting_count")
    od_amnt_invoiced = fields.Float(string="Customer Invoice Amount",compute="od_get_total_invoice")
    od_amnt_invoiced2 = fields.Float(string="Customer Invoice Amount",compute="od_get_total_invoice")
    od_amnt_purchased = fields.Float(string="Supplier Purchase Amount",compute="od_get_total_purchase")
    od_amnt_purchased2 = fields.Float(string="Supplier Purchase Amount",compute="od_get_total_purchase")
