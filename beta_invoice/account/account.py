# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time

import openerp
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools.safe_eval import safe_eval as eval

import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class account_account(osv.osv):
    
    _inherit = "account.account"
    def _check_moves(self, cr, uid, ids, method, context=None):
        line_obj = self.pool.get('account.move.line')
        account_ids = self.search(cr, uid, [('id', 'child_of', ids)], context=context)

        if line_obj.search(cr, uid, [('account_id', 'in', account_ids)], context=context):
            if method == 'write':
                pass
#                 raise osv.except_osv(_('Error!'), _('You cannot deactivate an account that contains journal items.'))
            elif method == 'unlink':
                raise osv.except_osv(_('Error!'), _('You cannot remove an account that contains journal items.'))
        #Checking whether the account is set as a property to any Partner or not
        values = ['account.account,%s' % (account_id,) for account_id in ids]
        partner_prop_acc = self.pool.get('ir.property').search(cr, uid, [('value_reference','in', values)], context=context)
        if partner_prop_acc:
            return True
#             raise osv.except_osv(_('Warning!'), _('You cannot remove/deactivate an account which is set on a customer or supplier.'))
        return True
    def _check_allow_code_change(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('account.move.line')
        
        for account in self.browse(cr, uid, ids, context=context):
            if account.note == '#re':
                return True
            account_ids = self.search(cr, uid, [('id', 'child_of', [account.id])], context=context)
            if line_obj.search(cr, uid, [('account_id', 'in', account_ids)], context=context):
                raise osv.except_osv(_('Warning !'), _("You cannot change the code of account which contains journal items!"))
        return True