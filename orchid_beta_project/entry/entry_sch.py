# -*- coding: utf-8 -*-
from openerp import models, fields, api
from pprint import pprint
from datetime import datetime
import openerp.addons.decimal_precision as dp


class entry_sch(models.model):
    _name = 'od.entry.sch'
    partner_ids = fields.Many2many('res.partner','entry_sch_part','en_sch_id','partner_id',string="Partner",required=True)
    entry_id = fields.Many2one('account.move',string="Opening Entry")
    account_ids = fields.Many2many('account.account','entry_sch_accounts','en_sch_id','account_id',string="Accounts",required=True)
    
    
    