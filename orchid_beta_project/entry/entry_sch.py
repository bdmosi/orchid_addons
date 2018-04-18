# -*- coding: utf-8 -*-
from openerp import models, fields, api,_
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp


class entry_sch(models.Model):
    _name = 'od.entry.sch'
    _rec_name ='move_id'
    partner_ids = fields.Many2many('res.partner','entry_sch_part','en_sch_id','partner_id',string="Partner")
    move_id = fields.Many2one('account.move',string="Opening Entry")
    account_ids = fields.Many2many('account.account','entry_sch_accounts','en_sch_id','account_id',string="Accounts")
    branch_id = fields.Many2one('od.cost.branch',string="Branch")
    
    
    @api.multi
    def show_entries(self):
        partner_ids = [pr.id for pr in self.partner_ids]
        account_ids = [pr.id for pr in self.account_ids]
        move_id  = self.move_id and self.move_id.id
        domain =[]
        if move_id:
            domain +=[('move_id','=',move_id)]
        if partner_ids:
            domain +=[('partner_id','in',partner_ids)]
        if account_ids:
            domain +=[('account_id','in',account_ids)]
            
        entry_pool = self.env['account.move.line']
        entry_ids = [ent.id for ent in entry_pool.search(domain)]
        
        model_data = self.env['ir.model.data']
        # Select the view
        tree_view = model_data.get_object_reference( 'orchid_beta_project', 'view_account_movelineb_sch_tree')
        search_view = model_data.get_object_reference('orchid_beta_project', 'view_sch_entry_b_moveline_search')
        domain =[('id','in',entry_ids)]
        value = {
                'name': _('Entries'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'account.move.line',
                'domain' : domain,
                'views': [ (tree_view and tree_view[1] or False, 'tree')],
                'type': 'ir.actions.act_window',
                'search_view_id': search_view and search_view[1] or False,
        }
        return value
    @api.one 
    def update_branch(self):
        partner_ids = [pr.id for pr in self.partner_ids]
        account_ids = [pr.id for pr in self.account_ids]
        move_id  = self.move_id and self.move_id.id
        branch_id = self.branch_id and self.branch_id.id 
        domain =[]
        if move_id:
            domain +=[('move_id','=',move_id)]
        if partner_ids:
            domain +=[('partner_id','in',partner_ids)]
        if account_ids:
            domain +=[('account_id','in',account_ids)]
            
        entry_pool = self.env['account.move.line']
        entry_ids =entry_pool.search(domain)
        entry_ids.write({'od_branch_id':branch_id})
        
    
    