# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning

class Procedures(models.Model):
    
    _name = 'beta.procedures'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    name = fields.Char('Name')
    image = fields.Binary(string='Attached Image')
    description = fields.Text()
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    
class Structures(models.Model):
    
    _name = 'beta.structures'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    name = fields.Char('Name')
    image = fields.Binary(string='Attached Image')
    description = fields.Text()
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)

class RoleDescription(models.Model):
    
    _name = 'role.description'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    name = fields.Char('Name')
    image = fields.Binary(string='Attached Image')
    description = fields.Text()
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)