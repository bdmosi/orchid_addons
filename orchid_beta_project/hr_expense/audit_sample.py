# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
from openerp.exceptions import Warning
class audit_sample(models.Model):
    _name ="audit.sample"
    
    @api.one 
    @api.depends('post_sale_sample_line')
    def _get_avg_score(self):
        if self.post_sale_sample_line:
            self.avg_score = sum([x.score for x in self.post_sale_sample_line ])/float(len([x.score for x in self.post_sale_sample_line ]))
    name = fields.Char(string="Name",required=True)
    date_start = fields.Date(string="Date Start")
    date_end = fields.Date(string="Date End")
    aud_temp_id = fields.Many2one('audit.template',string="Audit Template")
    type = fields.Selection([('post_sales','Post Sales'),('pre_sales','Pre-Sales'),('bdm','Business Development Manager'),('ttl','Technical Team Lead')],string="Type")
    employee_id = fields.Many2one('hr.employee',string="Employee")
    method = fields.Text(string="Method")
    avg_score = fields.Float(string="Monthly Avg Score",compute="_get_avg_score")
    post_sale_sample_line = fields.One2many('post.sales.comp.sample','sample_id',string="Post Sales Samples")
    
    
class post_sales_comp_sample(models.Model):
    _name ='post.sales.comp.sample'
    sample_id = fields.Many2one('audit.sample',string="Sample",ondelete="cascade")
    task_id = fields.Many2one('project.task',string="Activity",ondelete="cascade")
    score = fields.Float(string="Score")
    
