# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning

class Procedures(models.Model):
    
    _name = 'beta.procedures'
    _description = "Beta Procedures"
    _order = 'sequence'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    name = fields.Char('Name')
    image = fields.Binary(string='Attached Image')
    description = fields.Text()
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)
    
class Structures(models.Model):
    
    _name = 'beta.structures'
    _description = "Beta Structures"
    _order = 'sequence'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    name = fields.Char('Name')
    image = fields.Binary(string='Attached Image')
    description = fields.Text()
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)
    
class RoleDescription(models.Model):
    
    _name = 'role.description'
    _description = "Role Description"
    _order = 'sequence'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    name = fields.Char('Name')
    image = fields.Binary(string='Attached Image')
    description = fields.Text()
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)
    
class BetaKPI(models.Model):
    
    _name = 'beta.kpi'
    _description = "Beta KPIs"
    _order = 'sequence'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    name = fields.Char('Name')
    image = fields.Binary(string='Attached Image')
    description = fields.Text()
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)
    
