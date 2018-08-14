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
    
class BetaDocs(models.Model):
    
    _name = 'beta.docs'
    _description = "Beta Documents"
    _order = 'sequence'
    
    def od_get_company_id(self):
        return self.env.user.company_id
    
    
    name = fields.Char('Reference')
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    attach_file = fields.Binary('Attach File')
    issue_date = fields.Date('Issue Date')
    expiry_date = fields.Date('Expiry Date')
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)

    
class BetaVideos(models.Model):
    
    _name = 'beta.videos'
    _description = "Beta Videos"
    _order = 'sequence'
    
    @api.one 
    @api.depends('url')
    def _get_link(self):
        self.url2 = self.url
    
    name = fields.Char('Reference')
    url = fields.Char('URL')
    url2 = fields.Char('Video Link',compute="_get_link")
    issue_date = fields.Date('Issue Date')
    expiry_date = fields.Date('Expiry Date')
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)
    
