# -*- coding: utf-8 -*-

from openerp import models,fields,api,_
from datetime import datetime,date,timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning
class crm_helpdesk(models.Model):
    _inherit ="crm.helpdesk"
    _rec_name = 'od_number'
    
    def od_send_mail(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        template_id = ir_model_data.get_object_reference('orchid_beta_project', template)[1]
        record_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,record_id, force_send=True)
        return True
    def od_escalation_schedule(self,cr,uid,context=None):
        print "escalation schedule start>>>>>>>>>>>>>>>>>>>>>>>>"
        today = date.today()
        today = datetime.strftime(today,DF)
        data_ids = self.search(cr,uid,[('state','=','open')])
        for data in self.browse(cr,uid,data_ids):
            deadline = data.date_deadline
            if deadline < today:
                company_id = data.company_id and data.company_id.id
                template = 'od_escalation_template'
                if company_id == 6:
                    template = template + '_saudi'
                print "started send mainl>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
                self.od_send_mail_old_api(cr,uid,data.id,template)
    
    def od_send_mail_old_api(self,cr,uid,ids,template):
        print "trying to send mail"
        ir_model_data = self.pool['ir.model.data']
        email_obj = self.pool.get('email.template')
        template_id = ir_model_data.get_object_reference(cr,uid,'orchid_beta_project', template)[1]
        print "emila temlp id>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",template_id
        email_obj.send_mail(cr,uid,template_id,ids, force_send=True)
        return True
    
    def od_get_tasks(self):
        task_pool = self.env['project.task']
        hd_id = self.id
        task_search_domain = [('od_help_desk_issue_id','=',hd_id)]
        tasks = task_pool.search(task_search_domain)
        return tasks
    @api.multi
    def od_btn_open_tasks(self):
        tasks = self.od_get_tasks()
        task_ids = [task.id for task in tasks]
        domain = [('id','in',task_ids)]
        hd_id = self.id
        ctx = {'default_od_help_desk_issue_id':hd_id}
        return {
            'domain':domain,
            'context':ctx,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
        }
    @api.one
    def od_get_task_count(self):
        tasks = self.od_get_tasks()
        task_count = len(tasks)
        self.od_task_count = task_count
    @api.multi
    def od_btn_open_timsheet_for_helpdesk(self):
        work_pool = self.env['project.task.work']
        tasks = self.od_get_tasks()
        task_ids = [task.id for task in tasks]
        work_search_dom = [('task_id','in',task_ids)]
        all_timesheet_ids = [work.hr_analytic_timesheet_id for work in work_pool.search(work_search_dom)]
        timesheet_ids = []
        for timesheet in all_timesheet_ids:
            if timesheet:
                timesheet_ids.append(timesheet.id)
        domain = [('id','in',timesheet_ids)]
        return {
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.analytic.timesheet',
            'type': 'ir.actions.act_window',
        }

    @api.one
    def od_get_timesheet_amount(self):
        work_pool = self.env['project.task.work']
        tasks = self.od_get_tasks()
        task_ids = [task.id for task in tasks]
        work_search_dom = [('task_id','in',task_ids)]
        all_timesheet_ids = [work.hr_analytic_timesheet_id for work in work_pool.search(work_search_dom)]
        timesheet_amounts = []
        for timesheet in all_timesheet_ids:
            if timesheet:
                timesheet_amounts.append(timesheet.normal_amount)
        amount = sum(timesheet_amounts)
        self.od_timesheet_amount = amount
    @api.model
    def create(self,vals):
        vals['od_number'] = self.env['ir.sequence'].get('crm.helpdesk') or '/'
        if vals.get('categ_id',False) ==17 and not vals.get('od_prev_create'):
            raise Warning("You Can Only Create Preventive Maintenance through Schedule in Analytic, Please Contact Accounts/Finance Team For this")
        if vals.get('categ_id',False) == 16:
            now = str(datetime.now() + timedelta(days=5))
            vals['date_deadline'] = now[:10]
        
        return super(crm_helpdesk,self).create(vals)
    
    @api.multi 
    def write(self,vals):
        od_prev_create = self.od_prev_create
        categ_id = self.categ_id and self.categ_id.id or vals.get('categ_id',False)
        if vals.get('categ_id',False) == 17:
            raise Warning("You Can Only Create Preventive Through Schedule From Analytic,Please Contact Accounts/Finance Team For this")
        if vals.get('categ_id',False) ==17 and not od_prev_create:
            raise Warning("You Can Only Create Preventive Maintenance through Schedule in Analytic, Please Contact Accounts/Finance Team For this")
        if vals.get('date_deadline') and categ_id in (17,16) and not vals.get('od_deadline_change',False):
            raise Warning("You Are Not Allowed to Change the Deadline Date For Remedial and Preventive,Please Discard")
        if vals.get('categ_id',False) == 16:
            create_date = self.create_date
            deadline =str(datetime.strptime(create_date, '%Y-%m-%d %H:%M:%S') + timedelta(days=5))
            vals['date_deadline'] = deadline[:10]
            vals['od_deadline_change'] = True
        if vals.get('state',False) == 'done':
            now =str(datetime.now())
            vals['close_date'] =now[:10]
        return super(crm_helpdesk,self).write(vals)
        
    
    
    
    @api.one
    @api.depends('categ_id','date_deadline','close_date')
    def _get_hd_kpi(self):
        categ_id = self.categ_id and self.categ_id.id
        if categ_id in (16,17):
            close_date = self.close_date
            deadline = self.date_deadline 
            if close_date <= deadline:
                self.od_hd_kpi = 100.0
         
    
    @api.onchange('od_organization_id')
    def onchange_organization_id(self):
        if self.od_organization_id:
            section_id = self.od_organization_id and self.od_organization_id.section_id and self.od_organization_id.section_id.id or False
            self.section_id = section_id
    od_timesheet_amount = fields.Float(string='Timesheet Amount',compute="od_get_timesheet_amount")
    od_task_count = fields.Integer(string="Task Count",compute="od_get_task_count")
    od_number = fields.Char(string="Help Desk Issue Sequence",default="/")
    od_organization_id = fields.Many2one('res.partner',string="Organization")
    od_mobile_number = fields.Char(string="Mobile Number",related="partner_id.mobile",readonly=True)
    od_landline = fields.Char(string="Land Line",related="partner_id.phone",readonly=True)
    od_brand_ids = fields.Many2many('od.product.brand','rel_helpdesk_product_brand','helpdesk_id','brand_id',string="Brands")
    od_subgroup_id = fields.Many2one('od.product.sub.group',string="Sub Group")
    od_activity_lines = fields.One2many('od.helpdesk.activity.log','hd_id',string="Work Logs")
    od_eqp_lines = fields.One2many('od.helpdesk.eqp.log','hd_id',string="Equipment Logs")
    od_summary_lines = fields.One2many('od.helpdesk.summary.log','hd_id',string="Summary")
    od_project_id = fields.Many2one('project.project',string="Project")
    od_sch_id = fields.Many2one('preventive.maint.schedule',string="Schedule")
    od_prev_create = fields.Boolean(string="Preventive Maint Create")
    od_deadline_change = fields.Boolean("Change Deadline")
    close_date = fields.Date(string="Closing Date")
    od_hd_kpi = fields.Float(string="KPI Score",compute="_get_hd_kpi")
class od_helpdesk_activity_log(models.Model):
    _name = "od.helpdesk.activity.log"
    _order ='date'
    hd_id = fields.Many2one('crm.helpdesk',string="Help Desk",ondelete="cascade")
    name = fields.Text(string="Notes")
    date = fields.Datetime(string="Date",default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class od_helpdesk_eqp_log(models.Model):
    _name = "od.helpdesk.eqp.log"
    _order ='date'
    hd_id = fields.Many2one('crm.helpdesk',string="Help Desk",ondelete="cascade")
    product_id = fields.Many2one('product.product',string="Equipment")
    name = fields.Text(string="Notes")
    date = fields.Datetime(string="Date",default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class od_helpdesk_summary_log(models.Model):
    _name = "od.helpdesk.summary.log"
    _order ='date'
    hd_id = fields.Many2one('crm.helpdesk',string="Help Desk",ondelete="cascade")
    name = fields.Text(string="Notes")
    date = fields.Datetime(string="Date",default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
