# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

class account_invoice(models.Model):
    _inherit = "account.invoice"
    od_discount = fields.Float(string='Discount',digits= dp.get_precision('Account'))
    od_discount_acc_id = fields.Many2one('account.account', string='Dis. Account', readonly=True, states={'draft': [('readonly', False)]},       help="The account used for write of discount.")

    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount','od_discount')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line) 
        self.amount_tax = sum(line.amount for line in self.tax_line)
        self.amount_total = self.amount_untaxed + self.amount_tax - self.od_discount

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        
        def get_currency_check(from_currncy,to_currecny):
            return from_currncy != to_currecny
        
        cur_check = get_currency_check(self.currency_id, self.company_id.currency_id)
        amt_currency_id = False
        amount_currency = 0.0
        if cur_check:
            amt_currency_id = self.currency_id and self.currency_id.id
        
        if self.type == 'in_invoice' and self.od_discount > 0:
            new_line=[]
            discount = self.od_discount
            from_currency = self.currency_id
            discount = from_currency.compute(discount,self.company_id.currency_id)
            for line in move_lines:
                if line[2].get('credit'):
                    line[2]['credit'] = line[2].get('credit') - discount
                    if cur_check:
                        line[2]['amount_currency'] = line[2].get('amount_currency') + self.od_discount #-ve sign when credit
                    break
            if cur_check:
                amount_currency =-1 * self.od_discount
            vals={'analytic_account_id': False, 'tax_code_id': False, 'analytic_lines': [], 'tax_amount': False, 'name': u'Supplier Discount', 'ref': False, 'asset_id': False, 
                  'currency_id': amt_currency_id, 'credit': discount, 'product_id': False, 'date_maturity': self.date_due, 'debit': 0, 'date': self.date_invoice, 'amount_currency': amount_currency, 'product_uom_id': False, 'quantity': 1.0, 'partner_id': self.partner_id.id, 'account_id': self.od_discount_acc_id and self.od_discount_acc_id.id or False
                }
            move_lines.append((0,0,vals))  
        if self.type == 'out_invoice' and self.od_discount > 0:
            discount = self.od_discount
            from_currency = self.currency_id
            if cur_check:
                discount = from_currency.compute(discount,self.company_id.currency_id)             
            for line in move_lines:
                if line[2].get('debit'):
                    line[2]['debit'] = line[2].get('debit') - discount
                    if cur_check:
                        line[2]['amount_currency'] = line[2].get('amount_currency') + self.od_discount
                    break
            if cur_check:
                amount_currency = self.od_discount
            vals={'analytic_account_id': False, 'tax_code_id': False, 'analytic_lines': [], 
                  'tax_amount': False, 'name': u'Customer Discount', 'ref': False, 'asset_id': False, 
                  'currency_id': amt_currency_id, 'debit':discount, 'product_id': False, 'date_maturity': self.date_due, 'credit': 0, 'date': self.date_invoice, 'amount_currency': amount_currency, 'product_uom_id': False, 'quantity': 1.0, 'partner_id': self.partner_id.id, 'account_id': self.od_discount_acc_id and self.od_discount_acc_id.id or False
                }
            move_lines.append((0,0,vals))    
        return super(account_invoice, self).finalize_invoice_move_lines(move_lines)

