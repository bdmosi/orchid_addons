# -*- coding: utf-8 -*-

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools import amount_to_text_en
from . import amount_to_ar
from pprint import pprint
from openerp import tools


class account_invoice(models.Model):
    _inherit = "account.invoice"
    @api.multi    
    def amount_to_text_en(self, amount, currency):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency=currency)        
        convert_amount_in_words = convert_amount_in_words.replace('Cent', 'Fil')                  
        return convert_amount_in_words
    
    @api.multi    
    def amount_to_text_ar(self, amount, currency):
        convert_amount_in_words = amount_to_ar.amount_to_text_ar(amount, currency='')        
        return convert_amount_in_words
    
    
    
    
    
    @api.constrains('gov_alternate_line')
    def _check_gov_alternate_line(self):
        """ Ensure the Amount"""
        if self.gov_alternate_line:
            invoice_amount = self.amount_total
            alt_amount = sum([line.total_amount for line in self.gov_alternate_line])
            diff = invoice_amount - alt_amount 
            if abs(diff) >5.0:
                raise Warning("Please Make Sure Government Alternate Line Total and Invoice Total Difference Cannot be Greater than 5.0")
    
    
    
    od_analytic_account = fields.Many2one('account.analytic.account',string='Analytic Account') 
    reason_for_credit_note = fields.Char(string="Reason For Credit Note")
    reason_for_debit_note = fields.Char(string="Reason For Debit Note")
    bank1_id = fields.Many2one('res.partner.bank',string="Bank 1",readonly=True,states={'draft':[('readonly',False)]})
    bank2_id = fields.Many2one('res.partner.bank',string="Bank 2",readonly=True,states={'draft':[('readonly',False)]})
    payment_term_detail_line = fields.One2many('invoice.beta.payment.terms','invoice_id',string="Payment Term Details",readonly=True,states={'draft':[('readonly',False)]})
    gov_alternate_line = fields.One2many('invoice.alternate.line','invoice_id',string="Alternate Line")
   
    od_original_invoice_id = fields.Many2one('account.invoice',string="Original Invoice")
    od_cost_sheet_id = fields.Many2one('od.cost.sheet',string="Cost Sheet",readonly=True)
    od_cost_centre_id =fields.Many2one('od.cost.centre',string='Cost Centre',readonly=True,states={'draft':[('readonly',False)]})
    od_branch_id =fields.Many2one('od.cost.branch',string='Branch',readonly=True,states={'draft':[('readonly',False)]})
    od_division_id = fields.Many2one('od.cost.division',string='Division',readonly=True,states={'draft':[('readonly',False)]})
    lead_id = fields.Many2one('crm.lead',string="Opportunity",related="od_cost_sheet_id.lead_id",readonly=True)
     
    od_sale_team_id = fields.Many2one('crm.case.section',string="Sale Team",related="lead_id.section_id",readonly=True)
    op_stage_id = fields.Many2one('crm.case.stage',string="Opp Stage",related="lead_id.stage_id",readonly=True)    
    op_expected_booking = fields.Date(string="Opp Expected Booking",related="lead_id.date_action",readonly=True)    
   
      
    fin_approved_date = fields.Datetime(string="Finance Approved Date",related="od_cost_sheet_id.approved_date",readonly=True)
    od_closing_date = fields.Date(string="Closing Date")
    bt_enable = fields.Boolean(string="Enable Payment Percentage",readonly=True,states={'draft':[('readonly',False)]})
    bt_pay_perc = fields.Float(string="Payment %",readonly=True,states={'draft':[('readonly',False)]})
    bt_supply_date = fields.Date(string="Supply Date",readonly=True,states={'draft':[('readonly',False)]})
    bt_po_ref = fields.Char(string="Client PO Ref",readonly=True,states={'draft':[('readonly',False)]})
#     bt_client_po_ref = fields.Char(string="Client PO Ref",readonly=True,states={'draft':[('readonly',False)]})
    
    
    
    @api.multi  
    def bt_apply_percent(self):
        bt_enable = self.bt_enable 
        bt_pay_perc = self.bt_pay_perc 
        for line in self.invoice_line:
            line.bt_enable = bt_enable 
            line.bt_pay_perc = bt_pay_perc
            
    
    
    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        print "invoice to movelines>>>>>>>>>>>>>>>>>>>>>>>",move_lines
        pprint(move_lines)
        od_cost_centre_id = self.od_cost_centre_id and self.od_cost_centre_id.id or False
        od_branch_id = self.od_branch_id and self.od_branch_id.id or False
        od_division_id = self.od_division_id and self.od_division_id.id or False
        if not od_cost_centre_id:
            od_cost_centre_id = (self.od_analytic_account and self.od_analytic_account.od_cost_centre_id and self.od_analytic_account.od_cost_centre_id.id) or (self.od_analytic_account and self.od_analytic_account.cost_centre_id and self.od_analytic_account.cost_centre_id.id)
        if not od_branch_id:
            od_branch_id = (self.od_analytic_account and self.od_analytic_account.od_branch_id and self.od_analytic_account.od_branch_id.id) or (self.od_analytic_account and self.od_analytic_account.branch_id and self.od_analytic_account.branch_id.id)
        if not od_division_id:
            od_division_id = (self.od_analytic_account and self.od_analytic_account.od_division_id and self.od_analytic_account.od_division_id.id) or (self.od_analytic_account and self.od_analytic_account.division_id and self.od_analytic_account.division_id.id)

        if not (od_cost_centre_id  and od_branch_id):
            raise Warning("Need to Fill Cost center and Branch")
        for _,_,move_line in move_lines:
            move_line.update({
                'od_cost_centre_id':od_cost_centre_id,
                'od_branch_id':od_branch_id,
                'od_division_id':od_division_id
                })
             
       
        return super(account_invoice, self).finalize_invoice_move_lines(move_lines)




class account_invoice_tax(models.Model):
    _inherit = "account.invoice.tax"
    @api.v8
    def compute(self, invoice):
        tax_grouped = {}
        currency = invoice.currency_id.with_context(date=invoice.date_invoice or fields.Date.context_today(invoice))
        company_currency = invoice.company_id.currency_id
        for line in invoice.invoice_line:
            price_unit = line.price_unit 
            bt_enable = line.bt_enable 
            bt_pay_perc = line.bt_pay_perc
            if bt_enable:
                price_unit = price_unit * (bt_pay_perc/100.0)
            taxes = line.invoice_line_tax_id.compute_all(
                (price_unit * (1 - (line.discount or 0.0) / 100.0)),
                line.quantity, line.product_id, invoice.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'invoice_id': invoice.id,
                    'name': tax['name'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'base': currency.round(tax['price_unit'] * line['quantity']),
                }
                if invoice.type in ('out_invoice','in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_collected_id']
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['ref_base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['ref_tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_paid_id']

                # If the taxes generate moves on the same financial account as the invoice line
                # and no default analytic account is defined at the tax level, propagate the
                # analytic account from the invoice line to the tax line. This is necessary
                # in situations were (part of) the taxes cannot be reclaimed,
                # to ensure the tax move is allocated to the proper analytic account.
                if not val.get('account_analytic_id') and line.account_analytic_id and val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = currency.round(t['base'])
            t['amount'] = currency.round(t['amount'])
            t['base_amount'] = currency.round(t['base_amount'])
            t['tax_amount'] = currency.round(t['tax_amount'])

        return tax_grouped
    
    
class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"
    bt_enable = fields.Boolean(string="Enable Pay %")
    bt_pay_perc = fields.Float(string="Payment %")
    
    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_id', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id','bt_enable','bt_pay_perc')
    def _compute_price(self):
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        bt_enable = self.bt_enable
        if bt_enable:
            bt_pay_perc = self.bt_pay_perc
            price = price * (bt_pay_perc/100.0)
        taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = taxes['total']
        if self.invoice_id:
            self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)

class invoice_beta_payment_terms(models.Model):
    _name = "invoice.beta.payment.terms"
    invoice_id = fields.Many2one('account.invoice',string="Invoice",ondelete='cascade')
    name = fields.Char(string="Payment Term")


class invoice_alternate_line(models.Model):
    _name = "invoice.alternate.line"
    
    
    @api.one 
    @api.depends('unit_price','quantity','tax_rate','bt_pay_perc','discount')
    def _compute_calc(self):
        total_bf_tax = self.unit_price * self.quantity
        bt_pay_perc = self.bt_pay_perc
        discount = self.discount
        if bt_pay_perc:
            total_bf_tax = total_bf_tax * (bt_pay_perc/100.0)
        if discount:
            total_bf_tax = total_bf_tax * (1 - (discount or 0.0) / 100.0)
        tax_rate = self.tax_rate /100.0
        tax_amount = total_bf_tax * tax_rate
        total_amount = total_bf_tax + tax_amount
        self.total_bf_tax = total_bf_tax 
        self.tax_amount = tax_amount 
        self.total_amount = total_amount
    
    
    invoice_id = fields.Many2one('account.invoice',string="Invoice",ondelete='cascade')
    name = fields.Text(string="Description Arabic")
    name2 = fields.Text(string="Description English")
    quantity = fields.Float(string="Quantity")
    unit_price = fields.Float(string="Unit Price",digits=dp.get_precision('Account'))
    total_bf_tax = fields.Float(string="Total Before Tax",compute="_compute_calc",digits=dp.get_precision('Account'))
    tax_rate =fields.Float(string="Tax Rate(%)")
    tax_amount =fields.Float(string="Tax Amount",compute="_compute_calc",digits=dp.get_precision('Account'))
    total_amount= fields.Float(string="Total Amount",compute="_compute_calc",digits=dp.get_precision('Account'))
    bt_enable = fields.Boolean(string="Enable Pay %")
    bt_pay_perc = fields.Float(string="Payment %")
    discount = fields.Float(string="Discount %",digits=dp.get_precision('Account'))
    
    