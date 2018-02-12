# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
class hr_expense_expense(models.Model):
    _inherit ="hr.expense.expense"

    od_payment_status = fields.Selection([('paid','Paid Fully'),('paid_partial','Paid Partially')],string="Interim Payment Status")
    od_payment_datetime = fields.Datetime(string="Interim Payment Date")
    od_paid_amount = fields.Float(string="Interim Paid Amount")
