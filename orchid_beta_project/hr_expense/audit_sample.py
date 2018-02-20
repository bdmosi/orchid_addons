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
        if avg_score >100.0:
            avg_score =100.0
        self.avg_score = avg_score    
    name = fields.Char(string="Name",required=True)
    date_start = fields.Date(string="Date Start")
    date_end = fields.Date(string="Date End")
    aud_temp_id = fields.Many2one('audit.template',string="Audit Template")
    type = fields.Selection([('post_sales','Post Sales'),('pre_sales','Pre-Sales Engineer'),
                             ('pre_sales_mgr','Pre-Sales Manager'),('bdm','Business Development Manager'),('ttl','Technical Team Leader')],string="Type")
    employee_id = fields.Many2one('hr.employee',string="Employee")
    method = fields.Text(string="Method")
    avg_score = fields.Float(string="Monthly Avg Score",compute="_get_avg_score")
    post_sale_sample_line = fields.One2many('post.sales.comp.sample','sample_id',string="Post Sales Samples")
    utl_sample_line = fields.One2many('ttl.utl.sample','sample_id',string="Utilization Component")
    ttl_fot_line = fields.One2many('ttl.ontime.sample','sample_id',string="Utilization FOT")
    comp_line = fields.One2many('component.line','sample_id',string="Component Line")
    opp_sample_line = fields.One2many('presale.opp.sample','sample_id',string="Presales Opp Samples")
    team_line = fields.One2many('team.score.line','sample_id',string="Team Score")



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

class post_sales_comp_sample(models.Model):
    _name ='post.sales.comp.sample'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    task_id = fields.Many2one('project.task',string="Activity",ondelete="cascade")
    score = fields.Float(string="Score")
    
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
    
    