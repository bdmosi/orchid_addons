# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
from openerp.exceptions import Warning
class audit_template(models.Model):
    _name ="audit.template"
    name = fields.Char(string="Name",required=True)
    type = fields.Selection([('post_sales','Post Sales'),('pre_sales','Pre-Sales'),('bdm','Business Development Manager'),('ttl','Technical Team Lead')],string="Type")
    desc  = fields.Text(string="Description")
    calc = fields.Text(string="Calculation Method")
    data_model = fields.Char(string="Data Model")
    
    
