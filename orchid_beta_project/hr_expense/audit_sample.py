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
        if avg_score >100.0 and self.type !='sales_acc_mgr':
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
                             ('pre_sales_mgr','Pre-Sales Manager'),('sales_acc_mgr','Sales Account Manager'),('bdm','Business Development Manager'),('ttl','Technical Team Leader')],string="Type",required=True)
    employee_id = fields.Many2one('hr.employee',string="Employee")
    method = fields.Text(string="Method")
    avg_score = fields.Float(string="Monthly Avg Score",compute="_get_avg_score")
    post_sale_sample_line = fields.One2many('post.sales.comp.sample','sample_id',string="Post Sales Samples")
    utl_sample_line = fields.One2many('ttl.utl.sample','sample_id',string="Utilization Component")
    ttl_fot_line = fields.One2many('ttl.ontime.sample','sample_id',string="Utilization FOT")
    comp_line = fields.One2many('component.line','sample_id',string="Component Line")
    opp_sample_line = fields.One2many('presale.opp.sample','sample_id',string="Presales Opp Samples")
    team_line = fields.One2many('team.score.line','sample_id',string="Team Score")
    commit_gp_line = fields.One2many('commit.gp.sample.line','sample_id',string="Commit GP Samples")
    commit_gp_locked = fields.Boolean(string="Commit GP Sample Generation Locked")
    achieved_gp_line = fields.One2many('achieved.gp.sample.line','sample_id',string="Commit GP Samples")
    commit_total = fields.Float(string="Commit Total",compute="_get_total")
    achieved_total = fields.Float(string="Achieved Total",compute="_get_total")



class CommitGpSample(models.Model):
    _name ='commit.gp.sample.line'
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
    
class AchievedGpSample(models.Model):
    _name ='achieved.gp.sample.line'
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


class TeamScore(models.Model):
    _name ='team.score.line'
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
    utl = fields.Float(string="Utilization")
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
    
    