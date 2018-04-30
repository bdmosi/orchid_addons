# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
from openerp.exceptions import Warning
class audit_sample(models.Model):
    _name ="audit.sample"
    
    @api.one 
    @api.depends('post_sale_sample_line')
    def _get_avg_score(self):
#         if self.post_sale_sample_line and self.type=='post_sales':
#             self.avg_score = sum([x.score for x in self.post_sale_sample_line ])/float(len([x.score for x in self.post_sale_sample_line ]))
#         if self.type !='post_sales':
        avg_score = sum([x.final_score for x in self.comp_line])
        if avg_score >100.0 and self.type not in ('sales_acc_mgr','pmo','hoo'):
            avg_score =100.0
        self.avg_score = avg_score
        
        
    @api.one 
    @api.depends('commit_gp_line','achieved_gp_line')
    def _get_total(self):
        self.commit_total = sum([x.gp for x in self.commit_gp_line]) 
        self.achieved_total =  sum([x.gp for x in self.achieved_gp_line])  
    name = fields.Char(string="Name",required=True)
    date_start = fields.Date(string="Date Start")
    date_end = fields.Date(string="Date End")
    aud_temp_id = fields.Many2one('audit.template',string="Audit Template")
        
    type = fields.Selection([('post_sales','Post Sales'),('pre_sales','Pre-Sales Engineer'),
                             ('pre_sales_mgr','Pre-Sales Manager'),('sales_acc_mgr','Sales Account Manager'),
                             ('service_sale_spl','Service Sale Specialist'),
                             ('sm','Sales Manager'),
                             ('bdm','BDM'), ('bdm_sec','BDM-SEC'),('bdm_net','BDM-NET-DC'),('ttl','Technical Team Leader'),
                             ('pm','Project Manager'),('pmo','PMO Director'),('pdm','Project Department Manager'),
                             ('tc','Technology Consultant'),('sde','Service Desk Engineer'),('sdm','Service Desk Manager'),
                             ('hoo','Head Of Operation'),
                             ],string="Type",required=True)
    
    employee_id = fields.Many2one('hr.employee',string="Employee")
    company_id = fields.Many2one('res.company',string="Company",related='employee_id.company_id',store=True)
    method = fields.Text(string="Method")
    avg_score = fields.Float(string="Monthly Avg Score",compute="_get_avg_score")
    post_sale_sample_line = fields.One2many('post.sales.comp.sample','sample_id',string="Post Sales Samples")
    utl_sample_line = fields.One2many('ttl.utl.sample','sample_id',string="Utilization Component")
    ttl_fot_line = fields.One2many('ttl.ontime.sample','sample_id',string="Utilization FOT")
    comp_line = fields.One2many('component.line','sample_id',string="Component Line")
    opp_sample_line = fields.One2many('presale.opp.sample','sample_id',string="Presales Opp Samples")
    team_line = fields.One2many('team.score.line','sample_id',string="Team Score")
    team_day_line = fields.One2many('team.day.line','sample_id',string="Team Score")
    team_hd_line = fields.One2many('team.hd.line','sample_id',string="Team Score")
    commit_gp_line = fields.One2many('commit.gp.sample.line','sample_id',string="Commit GP Samples")
    commit_gp_locked = fields.Boolean(string="Commit GP Sample Generation Locked")
    achieved_gp_line = fields.One2many('achieved.gp.sample.line','sample_id',string="Commit GP Samples")
    commit_total = fields.Float(string="Commit Total",compute="_get_total")
    achieved_total = fields.Float(string="Achieved Total",compute="_get_total")
    utilization = fields.Float(string="Utilization")
    target = fields.Float(string="Monthly Target")
    planned_invoice_line = fields.One2many('planned.analytic.invoice.line','sample_id',string="Planned Invoices")
    actual_invoice_line = fields.One2many('actual.analytic.invoice.line','sample_id',string="Actual Invoices")
    dayscore_line = fields.One2many('pm.dayscore.line','sample_id',string="Details")
    sde_day_score_line = fields.One2many('sde.dayscore.line','sample_id',string="Details")
    cost_control_line = fields.One2many('pm.cost.control.line','sample_id',string="Details")
    invoice_schedule_line = fields.One2many('pm.invoice.schedule.line','sample_id',string="Details")
    pm_sch_line = fields.One2many('pm.sch.control.line','sample_id',string="Details")
    
    compliance_line  =  fields.One2many('pm.compliance.line','sample_id',string="Details")
    bmd_costsheet_line = fields.One2many('bdm.costsheet.sample.line','sample_id',string="Details")
    bdm_sec_sample_line = fields.One2many('bdm.sec.sample.line','sample_id',string="Details")
    bdm_net_sample_line = fields.One2many('bdm.net.sample.line','sample_id',string="Details")
    
    bdm_sec_pip_sample_line = fields.One2many('bdm.sec.pip.sample.line','sample_id',string="Details")
    bdm_net_pip_sample_line = fields.One2many('bdm.net.pip.sample.line','sample_id',string="Details")

    pmo_open_project_line = fields.One2many('pmo.open.project.sample','sample_id',string="Details")
    pmo_closed_project_line = fields.One2many('pmo.closed.project.sample','sample_id',string="Details")
    tc_tech_comp_line =  fields.One2many('tc.tech.component.line','sample_id',string="Details")
    tc_presale_comp_line =  fields.One2many('tc.presale.comp.line','sample_id',string="Details")
    my_comp_line = fields.One2many('my.component.line','sample_id',string="Details")
    hd_line = fields.One2many('help.desk.sample.line','sample_id',string="Details")
    
    
    def update_closed_project_data(self,vals):
        pmo_closed_project = self.env['pmo.closed.project.sample']
        sample_id = self.id 
        for _,_,val in vals:
            analytic_id = val.get('analytic_id')
            closed_data = pmo_closed_project.search([('sample_id','=',sample_id),('analytic_id','=',analytic_id)])
            if closed_data:
                closed_data.write(val)
            else:
                pmo_closed_project.create(val)
        return True




class HelpDeskSample(models.Model):
    _name ='help.desk.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    hd_id = fields.Many2one('crm.helpdesk',string="Cost Sheet")
    score = fields.Float(string="Score")
     
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'crm.helpdesk',
                'res_id':self.hd_id and self.hd_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }


class my_component_line(models.Model):
    _name = 'my.component.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    name = fields.Char(string="Component")
    weight = fields.Float(string="Weight")
    score = fields.Float(string="Score")
    final_score = fields.Float(string="Final Score")


class tc_tech_component_line(models.Model):
    _name = 'tc.tech.component.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    name = fields.Char(string="Component")
    weight = fields.Float(string="Weight")
    score = fields.Float(string="Score")
    final_score = fields.Float(string="Final Score")
    
class tc_presale_comp_line(models.Model):
    _name = 'tc.presale.comp.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    name = fields.Char(string="Component")
    weight = fields.Float(string="Weight")
    score = fields.Float(string="Score")
    final_score = fields.Float(string="Final Score")
    


class PmoOpenProjects(models.Model):
    _name ="pmo.open.project.sample"
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    paid = fields.Float(string="Paid to Supplier")
    collected = fields.Float(string="Collected From Customer")
    project_value = fields.Float(string="Project Value")
    manpower_cost = fields.Float(string="Manpower Cost")
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.analytic.account',
                'res_id':self.analytic_id and self.analytic_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    
class PmoClosedProjects(models.Model):
    _name ="pmo.closed.project.sample"
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    paid = fields.Float(string="Paid to Supplier")
    manpower_cost = fields.Float(string="Manpower Cost")
    collected = fields.Float(string="Collected From Customer")
    project_value = fields.Float(string="Project Value")
    
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.analytic.account',
                'res_id':self.analytic_id and self.analytic_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    
class BdmSecuritySample(models.Model):
    _name ='bdm.sec.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    product_group_id = fields.Many2one('od.product.group',string="Product Group")
    sales = fields.Float(string="Sales")
    sales_aftr_disc = fields.Float(string="Sales After Discount")
    cost = fields.Float(string="Cost")
    profit = fields.Float(string="Profit")
    profit_percent = fields.Float(string="Profit Percentage")
    manpower_cost = fields.Float("Manpower Cost")
    gp = fields.Float(string="GP")
     
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }

class BdmSecurityPipSample(models.Model):
    _name ='bdm.sec.pip.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    product_group_id = fields.Many2one('od.product.group',string="Product Group")
    sales = fields.Float(string="Sales")
    sales_aftr_disc = fields.Float(string="Sales After Discount")
    cost = fields.Float(string="Cost")
    profit = fields.Float(string="Profit")
    profit_percent = fields.Float(string="Profit Percentage")
    manpower_cost = fields.Float("Manpower Cost")
    gp = fields.Float(string="GP")
    
     
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    
class BdmNetwrokSample(models.Model):
    _name ='bdm.net.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    product_group_id = fields.Many2one('od.product.group',string="Product Group")
    sales = fields.Float(string="Sales")
    sales_aftr_disc = fields.Float(string="Sales After Discount")
    cost = fields.Float(string="Cost")
    profit = fields.Float(string="Profit")
    profit_percent = fields.Float(string="Profit Percentage")
    manpower_cost = fields.Float("Manpower Cost")
    gp = fields.Float(string="GP")
    
     
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    

class BdmNetwrokPipSample(models.Model):
    _name ='bdm.net.pip.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    product_group_id = fields.Many2one('od.product.group',string="Product Group")
    sales = fields.Float(string="Sales")
    sales_aftr_disc = fields.Float(string="Sales After Discount")
    cost = fields.Float(string="Cost")
    profit = fields.Float(string="Profit")
    profit_percent = fields.Float(string="Profit Percentage")
    manpower_cost = fields.Float("Manpower Cost")
    gp = fields.Float(string="GP")
     
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    


class BdmCostsheetSample(models.Model):
    _name ='bdm.costsheet.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    gp = fields.Float(string="GP")
    
    
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }


class compliance_line(models.Model):
    _name ="pm.compliance.line"
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    score = fields.Float("Score From Project")
    sale_value = fields.Float(string="Sale Value")
    sale_value_percent = fields.Float("%Sale Value")
    weight = fields.Float(string="Weight")
    form_wt = fields.Float(string="Form Weight")
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.analytic.account',
                'res_id':self.analytic_id and self.analytic_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }


class invoice_schedule_line(models.Model):
    _name ="pm.invoice.schedule.line"
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    score = fields.Float("Score From Project")
    sale_value = fields.Float(string="Sale Value")
    sale_value_percent = fields.Float("%Sale Value")
    weight = fields.Float(string="Weight")
    form_wt = fields.Float(string="Form Weight")
    
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.analytic.account',
                'res_id':self.analytic_id and self.analytic_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }



class cost_control_line(models.Model):
    _name ="pm.cost.control.line"
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    score = fields.Float("Score From Project")
    gp_value = fields.Float(string="GP Value")
    gp_value_percent = fields.Float("%GP Value")
    weight = fields.Float(string="Weight")
    form_wt = fields.Float(string="Form Weight")
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.analytic.account',
                'res_id':self.analytic_id and self.analytic_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }

class PmScheduleControl(models.Model):
    _name ="pm.sch.control.line"
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    score = fields.Float("Score From Project")
    gp_value = fields.Float(string="GP Value")
    gp_value_percent = fields.Float("%GP Value")
    weight = fields.Float(string="Weight")
    form_wt = fields.Float(string="Form Weight")
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.analytic.account',
                'res_id':self.analytic_id and self.analytic_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }


class pm_dayscore(models.Model):
    _name ="pm.dayscore.line"
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    score = fields.Float("Score From Project")
    sale_value = fields.Float(string="Sale Value")
    sale_value_percent = fields.Float("%Sale Value")
    weight = fields.Float(string="Weight")
    form_wt = fields.Float(string="Form Weight")
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.analytic.account',
                'res_id':self.analytic_id and self.analytic_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
        
    @api.multi
    def btn_open_cst(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }


class sde_dayscore(models.Model):
    _name ="sde.dayscore.line"
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    score = fields.Float("Score From Project")
    sale_value = fields.Float(string="Sale Value")
    sale_value_percent = fields.Float("%Sale Value")
    weight = fields.Float(string="Weight")
    form_wt = fields.Float(string="Form Weight")
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.analytic.account',
                'res_id':self.analytic_id and self.analytic_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
        
    @api.multi
    def btn_open_cst(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }






class PlannedInvoices(models.Model):
    _name ='planned.analytic.invoice.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    
    amount = fields.Float(string="Planned Amount")

class ActualInvoices(models.Model):
    _name ='actual.analytic.invoice.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic/Project")
    invoice_id = fields.Many2one('account.invoice',string="Invoice")
    amount = fields.Float(string="Invoice Amount")

class CommitGpSample(models.Model):
    _name ='commit.gp.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    gp = fields.Float(string="GP")
    user_id = fields.Many2one('res.users',string="User")
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    
class AchievedGpSample(models.Model):
    _name ='achieved.gp.sample.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet")
    gp = fields.Float(string="GP")
    user_id = fields.Many2one('res.users',string="User")
    
    @api.multi
    def btn_open(self):
       
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'od.cost.sheet',
                'res_id':self.cost_sheet_id and self.cost_sheet_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }


class TeamScore(models.Model):
    _name ='team.score.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    user_id = fields.Many2one('res.users',string="User")
    score = fields.Float(string="Score")
    

class TeamDayLine(models.Model):
    _name ='team.day.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    user_id = fields.Many2one('res.users',string="User")
    score = fields.Float(string="Score")

class TeamHDLine(models.Model):
    _name ='team.hd.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    user_id = fields.Many2one('res.users',string="User")
    score = fields.Float(string="Score")


class presale_opp_sample(models.Model):
    _name ='presale.opp.sample'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    opp_id = fields.Many2one('crm.lead',string="Opportunity",ondelete="cascade")
    user_id = fields.Many2one('res.users',string="User")
    score = fields.Float(string="Score")
    
    @api.multi
    def btn_open(self):
        model_data = self.env['ir.model.data']
        form_view = model_data.get_object_reference('crm', 'crm_case_form_view_oppor')
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'crm.lead',
                'res_id':self.opp_id and self.opp_id.id or False,
                'views': [(form_view and form_view[1] or False, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',

            }

class post_sales_comp_sample(models.Model):
    _name ='post.sales.comp.sample'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    task_id = fields.Many2one('project.task',string="Activity",ondelete="cascade")
    score = fields.Float(string="Score")
    @api.multi
    def btn_open(self):
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'project.task',
                'res_id':self.task_id and self.task_id.id or False,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    
class ttl_utilization_sample(models.Model):
    _name ='ttl.utl.sample'
    user_id = fields.Many2one('res.users',string="User")
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    actual_time_spent = fields.Float(string="Actual Time Spent")
    available_time = fields.Float(string="Available Time")
    utl = fields.Float(string="Actual Utilization")
    planned_time = fields.Float(string="Planned Time")
    planned_utl = fields.Float(string="Planned Utilization")
class ttl_on_time_sample(models.Model):
    _name ='ttl.ontime.sample'
    user_id = fields.Many2one('res.users',string="User")
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    fot = fields.Float(string="Finished On Time")
class component_line(models.Model):
    _name = 'component.line'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    name = fields.Char(string="Component")
    weight = fields.Float(string="Weight")
    score = fields.Float(string="Score")
    final_score = fields.Float(string="Final Score")

    