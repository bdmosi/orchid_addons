# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
from openerp.exceptions import Warning
class audit_template(models.Model):
    _name ="audit.template"
    name = fields.Char(string="Name",required=True)
    type = fields.Selection([('post_sales','Post Sales'),('pre_sales','Pre-Sales Engineer'),
                             ('pre_sales_mgr','Pre-Sales Manager'),('sales_acc_mgr','Sales Account Manager'),
                             ('sm','Sales Manager'),
                             ('bdm','BDM'), ('bdm_sec','BDM-SEC'),('bdm_net','BDM-NET-DC'),('ttl','Technical Team Leader'),
                             ('pm','Project Manager'),('pmo','PMO Director'),('pdm','Project Department Manager'),
                             ('tc','Technology Consultant'),('sde','Service Desk Engineer'),('sdm','Service Desk Manager'),
                             ('hoo','Head Of Operation'),
                             ],string="Type",required=True)
    
    desc  = fields.Text(string="Description")
    calc = fields.Text(string="Calculation Method")
    data_model = fields.Char(string="Data Model")
    
    
