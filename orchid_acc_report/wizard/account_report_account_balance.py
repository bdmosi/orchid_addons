# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
import time
class account_balance_report(osv.osv_memory):
    _inherit = "account.balance.report"
    _columns = {
        'od_detail': fields.boolean('Detail'),
        'od_child':fields.selection([(1,'Level 1'),(2,'Level 2'),(3,'Level 3'),(4,'Level 4'),(5,'Level 5')],'Level'),
         'od_currency_id': fields.many2one('res.currency',string="Currency",domain="[('active','=',True)]")
#        'display_account': fields.selection([('all','All'), 
#                                            ('not_zero','With balance is not equal to 0'),
#                                            ],'Display Accounts', required=True),
#         'od_child':fields.boolean('Show Child'),
#       'od_print_template': fields.many2one('ir.actions.report.xml',string="Template",domain="[('report_name','=like','account.report_trialbalance%')]"),
    }
    _defaults = {
        'display_account': 'not_zero',
       # 'od_child': 4
    }
#     _defaults ={
# #                 'od_child':True
#                 }

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['od_detail','od_child','od_currency_id'])[0])
        print "dattaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",data
        if data['model'] == 'account.account':
            data['form']['id'] = data['ids'][0]
        if data['form'].get('od_detail'):
            return self.pool['report'].get_action(cr, uid, [], 'account.report_trialbalance_detail', data=data, context=context)
        return self.pool['report'].get_action(cr, uid, [], 'account.report_trialbalance', data=data, context=context)



    
