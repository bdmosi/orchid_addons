import time
from openerp.report import report_sxw
from openerp.addons.account.report.account_balance import account_balance
from openerp.tools.translate import _
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.osv import osv

class account_balance(account_balance):
    _inherit = 'report.account.account.balance'
    def __init__(self, cr, uid, name, context=None):
        super(account_balance, self).__init__(cr, uid, name, context=context)
        self.od_prev_result_acc = []
        self.od_next_result_acc = []
        self.context = context

    def lines(self, form, ids=None, done=None):
        od_next_done = done
        print "FFFFFFFFFFFf",form
        required_currency_id = form.get('od_currency_id') and form.get('od_currency_id')[0] or False
        def _process_child(accounts, disp_acc, parent):
                account_rec = [acct for acct in accounts if acct['id']==parent][0]
                currency_obj = self.pool.get('res.currency')
                acc_id = self.pool.get('account.account').browse(self.cr, self.uid, account_rec['id'])
                currency = acc_id.currency_id and acc_id.currency_id or acc_id.company_id.currency_id
                res = {
                    'id': account_rec['id'],
                    'type': account_rec['type'],
                    'code': account_rec['code'],
                    'name': account_rec['name'],
                    'level': account_rec['level'],
                    'debit': account_rec['debit'],
                    'credit': account_rec['credit'],
                    'balance': account_rec['balance'],
                    'parent_id': account_rec['parent_id'],
                    'bal_type': '',
                }
                self.sum_debit += account_rec['debit']
                self.sum_credit += account_rec['credit']

#Existing code is modified as sageer told all the account and balances are correct for if display account is all
                if disp_acc == 'movement':
#                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['credit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['debit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                    self.result_acc.append(res)
                elif disp_acc == 'not_zero':
#                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                    self.result_acc.append(res)
                else:
                    self.result_acc.append(res)
                if account_rec['child_id']:
                    for child in account_rec['child_id']:
                        _process_child(accounts,disp_acc,child)
#Custom code Prev
        def _od_prev_process_child(accounts, disp_acc, parent):
                account_rec = [acct for acct in accounts if acct['id']==parent][0]
                currency_obj = self.pool.get('res.currency')
                acc_id = self.pool.get('account.account').browse(self.cr, self.uid, account_rec['id'])
                currency = acc_id.currency_id and acc_id.currency_id or acc_id.company_id.currency_id
                res = {
                    'id': account_rec['id'],
                    'type': account_rec['type'],
                    'code': account_rec['code'],
                    'name': account_rec['name'],
                    'level': account_rec['level'],
                    'debit': account_rec['debit'],
                    'credit': account_rec['credit'],
                    'balance': account_rec['balance'],
                    'parent_id': account_rec['parent_id'],
                    'bal_type': '',
                }
                self.sum_debit += account_rec['debit']
                self.sum_credit += account_rec['credit']
                if disp_acc == 'movement':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['credit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['debit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                        self.od_prev_result_acc.append(res)
                elif disp_acc == 'not_zero':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                        self.od_prev_result_acc.append(res)
                else:
                    self.od_prev_result_acc.append(res)
                if account_rec['child_id']:
                    for child in account_rec['child_id']:
                        _od_prev_process_child(accounts,disp_acc,child)


#Custom code Next
        def _od_next_process_child(accounts, disp_acc, parent):
                account_rec = [acct for acct in accounts if acct['id']==parent][0]
                currency_obj = self.pool.get('res.currency')
                acc_id = self.pool.get('account.account').browse(self.cr, self.uid, account_rec['id'])
                currency = acc_id.currency_id and acc_id.currency_id or acc_id.company_id.currency_id
                res = {
                    'id': account_rec['id'],
                    'type': account_rec['type'],
                    'code': account_rec['code'],
                    'name': account_rec['name'],
                    'level': account_rec['level'],
                    'debit': account_rec['debit'],
                    'credit': account_rec['credit'],
                    'balance': account_rec['balance'],
                    'parent_id': account_rec['parent_id'],
                    'bal_type': '',
                }
                self.sum_debit += account_rec['debit']
                self.sum_credit += account_rec['credit']
                if disp_acc == 'movement':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['credit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['debit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                        self.od_next_result_acc.append(res)
                elif disp_acc == 'not_zero':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                        self.od_next_result_acc.append(res)
                else:
                    self.od_next_result_acc.append(res)
                if account_rec['child_id']:
                    for child in account_rec['child_id']:
                        _od_next_process_child(accounts,disp_acc,child)



        obj_account = self.pool.get('account.account')
        if not ids:
            ids = self.ids
        if not ids:
            return []
        if not done:
            done={}

        ctx = self.context.copy()

        ctx['fiscalyear'] = form['fiscalyear_id']
        if form['filter'] == 'filter_period':
            ctx['period_from'] = form['period_from']
            ctx['period_to'] = form['period_to']
        elif form['filter'] == 'filter_date':
            ctx['date_from'] = form['date_from']
            ctx['date_to'] =  form['date_to']
        ctx['state'] = form['target_move']
        parents = ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
        if child_ids:
            ids = child_ids
        accounts = obj_account.read(self.cr, self.uid, ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)
        for parent in parents:
                if parent in done:
                    continue
                done[parent] = 1
                _process_child(accounts,form['display_account'],parent)

#Custom Code Prev
        od_prev_ctx_date_to = form['date_from'] and (datetime.strptime(form['date_from'], DEFAULT_SERVER_DATE_FORMAT) - timedelta(days=1)) or False
        od_prev_ctx_date_from = form['date_from'] and datetime.strptime(form['date_from'], DEFAULT_SERVER_DATE_FORMAT) - timedelta(days=3650) or False
        od_next_ctx_date_from =  form['date_from'] and datetime.strptime(form['date_from'], DEFAULT_SERVER_DATE_FORMAT) - timedelta(days=3650) or False


        log_user = self.pool.get('res.users').browse(self.cr,self.uid,self.uid)
        company_id = log_user and log_user.company_id and log_user.company_id.id
        od_prev_ctx = ctx.copy()
        flag=False
        if form['filter'] == 'filter_date':
            od_prev_ctx['date_to'] = str(od_prev_ctx_date_to)
            od_prev_ctx['date_from'] = str(od_prev_ctx_date_from)
        elif form['filter'] == 'filter_period':
            od_period_obj = self.pool.get('account.period')
            crnt_fiscalyearyear = od_prev_ctx.get('fiscalyear')
#            search_periods = od_period_obj.search(self.cr,self.uid,[('od_sequence','=',0),('company_id','=',company_id)])
            search_periods = od_period_obj.search(self.cr,self.uid,[('special','=',True),('fiscalyear_id','=',crnt_fiscalyearyear),('company_id','=',company_id)])
            print "(((((Current financial year Opening period)))))",search_periods
            od_prev_ctx['period_from'] = search_periods and search_periods[0]
            od_prev_ctx['period_to'] = search_periods and search_periods[0] #Changed period to as the selected from period one date back period of the current selected period start_date
            #++++++++++++++++++++++++++++++++++++++++++++ code commented by jm ++++++++++
            # if od_prev_ctx['period_from'] !=  form['period_to'] :
            #     od_prev_ctx['period_to'] = form['period_from'] - 1
            #_____________________________________________________________________________

        parents = ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, od_prev_ctx)
        if child_ids:
            od_ids = child_ids
        accounts = obj_account.read(self.cr, self.uid, od_ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], od_prev_ctx)
#        print "accountssss\n\n\n!!!!!",accounts
        for parent in parents:
                if parent in done:
                    continue
                done[parent] = 1
                _od_prev_process_child(accounts,False,parent)


#Custom code for Next
        od_next_ctx = ctx.copy()
        if not od_next_done:
            od_next_done = {}
        if form['filter'] == 'filter_date':
            od_next_ctx['date_to'] = form['date_to']
            od_next_ctx['date_from'] = str(od_next_ctx_date_from)
        elif form['filter'] == 'filter_period':
            od_next_ctx['period_from'] = False
            od_period_obj = self.pool.get('account.period')
#            search_periods = od_period_obj.search(self.cr,self.uid,[('od_sequence','=',0),('company_id','=',company_id)])

            crnt_fiscalyearyear = od_next_ctx.get('fiscalyear')
            search_periods = od_period_obj.search(self.cr,self.uid,[('special','=',True),('fiscalyear_id','=',crnt_fiscalyearyear),('company_id','=',company_id)])
            
            od_next_ctx['period_from'] = search_periods and search_periods[0]

            od_next_ctx['period_to'] = form['period_to']
        parents = ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, od_next_ctx)
        if child_ids:
            od_ids = child_ids
        accounts = obj_account.read(self.cr, self.uid, od_ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], od_next_ctx)
        for parent in parents:
                if parent in od_next_done:
                    continue
                od_next_done[parent] = 1
                _od_next_process_child(accounts,False,parent)

        new_res=[]

        print "\nPrev Context:  ",od_prev_ctx
        print "\nCurrent COntext: ",ctx
        print "\n Next Context : ",od_next_ctx


        a=[x.get('id') for x in self.result_acc]
        b=[x.get('id') for x in self.od_prev_result_acc]
        c=[x.get('id') for x in self.od_next_result_acc]

        print "DDDDrestult a DDDDDDDD",len(a)
        print "DDDDDPrev b DDDDDDD",len(b)
        print "DDDDnext C DDDDDDDD",len(c)

#New Code tried to make the parent account
        extra_prev_res=[]

        for opening in self.result_acc:
            opening['opening_credit'],opening['opening_debit'],opening['opening_balance'],opening['opening_balance_cr'],opening['opening_balance_dr'] = 0,0,0,0,0
            opening['closing_credit'],opening['closing_debit'],opening['closing_balance'],opening['closing_balance_cr'],opening['closing_balance_dr'] = 0,0,0,0,0
            opening['balance_dr'],opening['balance_cr']=opening.get('credit') < 0 and opening.get('credit') or 0,opening.get('credit') > 0 and opening.get('credit') or 0
            for prev in self.od_prev_result_acc:
                if prev.get('id') == opening.get('id'):
                    opening['opening_credit']=prev.get('credit')
                    opening['opening_debit'] = prev.get('debit')
                    opening['opening_balance'] = prev.get('balance')

                    cr,dr = (prev.get('balance') < 0) and prev.get('balance')*-1 or 0,(prev.get('balance') > 0) and prev.get('balance') or 0
                    opening['opening_balance_dr'] = dr + 0.0000001
                    opening['opening_balance_cr'] = cr + 0.0000001

                elif prev.get('id') != opening.get('id'):
                    extra_prev_res.append(prev)
#                    
            for closing in self.od_next_result_acc:
                if closing.get('id') == opening.get('id'):
                    opening['closing_credit'] = closing.get('credit')
                    opening['closing_debit'] = closing.get('debit')
                    opening['closing_balance'],opening['closing_balance_cr'],opening['closing_balance_dr'] = closing.get('balance'),closing.get('balance') < 0 and closing.get('balance')*-1 or 0,closing.get('balance') > 0 and closing.get('balance') or 0


            new_res.append(opening)


        seen = set()
        new_l = []
        for d in new_res:
            t = tuple(d.items())
            if t not in seen:
                seen.add(t)
                new_l.append(d)
        return new_l


class report_trialbalance(osv.AbstractModel):
    _name = 'report.account.report_trialbalance'
    _inherit = 'report.abstract_report'
    _template = 'account.report_trialbalance'
    _wrapped_report_class = account_balance

class report_trialbalance_detail(osv.AbstractModel):
    _name = 'report.account.report_trialbalance_detail'
    _inherit = 'report.abstract_report'
    _template = 'account.report_trialbalance_detail'
    _wrapped_report_class = account_balance

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
