# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp.tools import float_round, float_is_zero, float_compare
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import dateutil.relativedelta
from datetime import date, timedelta,datetime
import openerp.addons.decimal_precision as dp
from collections import defaultdict
from math import exp,log10
from pprint import pprint
from openerp.osv import expression
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import logging

_logger = logging.getLogger(__name__)
class od_beta_closing_conditions(models.Model):
    _name ="od.beta.closing.conditions"
    name = fields.Char(string="Name")

class od_cost_sheet(models.Model):
    _name = 'od.cost.sheet'
    _description = 'Cost Sheet'
    _inherit = ['mail.thread']
    def cron_od_cost_sheet(self, cr, uid, context=None):
        context = dict(context or {})
        remind = []

        def fill_remind( domain):
            print "fill remind started"
            base_domain = []
            base_domain.extend(domain)
            cost_sheet_ids = self.search(cr, uid, base_domain, context=context)
            for costsheet in self.browse(cr,uid,cost_sheet_ids,context=context):
                if costsheet.state not in ('cancel','draft','submitted','design_ready'):
                    val = {'name':costsheet.name,'number':costsheet.number,
                        'customer':costsheet.od_customer_id and costsheet.od_customer_id.name or '',
                        'po_status':costsheet.po_status,'sale_person':costsheet.sales_acc_manager and costsheet.sales_acc_manager.name or '',
                        'owner':costsheet.reviewed_id and costsheet.reviewed_id.name or ''
                        }
                    remind.append(val)

        for company_id in [1,6]:
            remind = []
            fill_remind([('po_status', '!=', 'available'),('company_id','=',company_id),('state','not in',('draft','submitted','cancel','design_ready'))])
            template = 'od_cost_sheet_cron_email_template'
            if company_id == 6:
                template = template + '_saudi'
            template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'orchid_cost_sheet', template)[1]
            print "remind data>>>>>>>>>>>>>>>>>>>>>>",remind
            context["data"] = remind
            if remind:
                self.pool.get('email.template').send_mail(cr, uid, template_id, uid, force_send=True, context=context)

        return True

    @api.multi
    def od_btn_open_timsheet_for_opp(self):

        task_pool = self.env['project.task']
        work_pool = self.env['project.task.work']
        lead_id = self.lead_id and self.lead_id.id
        if lead_id:
            task_search_dom = [('od_opp_id','=',lead_id)]
            task_ids = [task.id for task in task_pool.search(task_search_dom)]
            work_search_dom = [('task_id','in',task_ids)]
            all_timesheet_ids = [work.hr_analytic_timesheet_id for work in work_pool.search(work_search_dom)]
            timesheet_ids = []
            for timesheet in all_timesheet_ids:
                if timesheet:
                    timesheet_ids.append(timesheet.id)
            domain = [('id','in',timesheet_ids)]
            return {
                'domain':domain,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'hr.analytic.timesheet',
                'type': 'ir.actions.act_window',
            }

    @api.one
    def od_get_timesheet_amount(self):
        task_pool = self.env['project.task']
        work_pool = self.env['project.task.work']
        lead_id = self.lead_id and self.lead_id.id
        if lead_id:
            task_search_dom = [('od_opp_id','=',lead_id)]
            task_ids = [task.id for task in task_pool.search(task_search_dom)]
            work_search_dom = [('task_id','in',task_ids)]
            all_timesheet_ids = [work.hr_analytic_timesheet_id for work in work_pool.search(work_search_dom)]
            timesheet_amounts = []
            for timesheet in all_timesheet_ids:
                if timesheet:
                    timesheet_amounts.append(timesheet.amount)
            amount = sum(timesheet_amounts)
            self.od_timesheet_amount = amount
    @api.multi
    def od_btn_open_account_move_lines(self):
        account_move_line = self.env['account.move.line']
        lead_id = self.lead_id and self.lead_id.id
        if lead_id:
            domain = [('od_opp_id','=',lead_id),('od_state','=','posted')]
            return {
                'domain':domain,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move.line',
                'type': 'ir.actions.act_window',
            }
    @api.one
    def od_get_lead_journal_amount(self):
        account_move_line = self.env['account.move.line']
        lead_id = self.id
        domain = [('od_opp_id','=',lead_id),('od_state','=','posted')]
        journal_lines = account_move_line.search(domain)
        amount = sum([mvl.debit for mvl in journal_lines])
        self.od_journal_amount = amount
    def default_get(self, cr, uid, fields, context=None):
        res = super(od_cost_sheet,self).default_get(cr,uid,fields,context=context)
        company_pool = self.pool.get('res.company')
        company_id = res.get('company_id')
        proposal_validity = "Proposal Validity Starting from its Date: 30 Days\nProposal Sales Currency: "
        if company_id:
            company_obj = company_pool.browse(cr,uid,company_id)
            currency_name = company_obj.currency_id and company_obj.currency_id.name or ''
            proposal_validity = proposal_validity + currency_name
            res['proposal_validity_duration'] = proposal_validity
        return res

    @api.multi
    def od_open_hr_expense_claim(self):
        hr_exp_line = self.env['hr.expense.line']
        lead_id = self.lead_id and self.lead_id.id
        domain = [('od_opp_id','=',lead_id),('od_state','not in',('draft','cancelled','confirm','second_approval'))]
        return {
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense.line',
            'type': 'ir.actions.act_window',
        }
    @api.one
    def od_get_hr_exp_claim_amount(self):
        hr_exp_line = self.env['hr.expense.line']
        lead_id = self.lead_id and self.lead_id.id
        domain = [('od_opp_id','=',lead_id),('od_state','not in',('draft','cancelled','confirm','second_approval'))]
        hr_exp_obj =hr_exp_line.search(domain)
        amount  = sum([hr.total_amount for hr in hr_exp_obj])
        self.od_hr_claim_amount = amount


    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','number'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['number']:
                name = '[' + record['number'] +'] ' + name
            res.append((record['id'], name))
        return res
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            domain = [('number', operator, name), ('name', operator, name)]
        else:
            domain = ['|', ('number', operator, name), ('name', operator, name)]
        ids = self.search(cr, user, expression.AND([domain, args]), limit=limit, context=context)
        return self.name_get(cr, user, ids, context=context)
    # @api.multi
    # @api.depends('name', 'number')
    # def name_get(self):
    #     result = []
    #     for sheet in self:
    #         number = self.number
    #         name = self.name
    #         result.append((sheet.id, '[%s]%s' % (number, name)))
    #     return result

    def grouped_brand_weight(self,res,all_brand_cost):
        result = []
        for item in res :
            check = False
            for r_item in result :
                if item['manufacture_id'] == r_item['manufacture_id'] :
                    check = True
                    total_sale = r_item['total_sale']
                    total_sale += item['total_sale']
                    r_item['total_sale'] = total_sale
                    total_cost = r_item['total_cost']
                    total_cost += item['total_cost']
                    r_item['total_cost'] = total_cost
            if check == False :
                item['all_brand_cost'] = all_brand_cost
                result.append( item )
        return result

    def get_brand_vals(self):
        res = []
        all_brand_cost = 0.0
        for line in self.mat_main_pro_line:
            res.append({'manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                'total_sale':line.line_price,
                'total_cost': line.line_cost_local_currency,
                })
            all_brand_cost += line.line_cost_local_currency
        result = self.grouped_brand_weight(res,all_brand_cost)
        return result
    
    
    @api.one
    def generate_brand_weight(self):
        vals = self.get_brand_vals()
        self.mat_brand_weight_line.unlink()
        self.mat_brand_weight_line = vals
        
        
    def grouped_prdgrp_weight(self,res,all_group_cost):
        result = []
        for item in res :
            check = False
            for r_item in result :
                if item['pdt_grp_id'] == r_item['pdt_grp_id'] :
                    check = True
                    total_sale = r_item['total_sale']
                    total_sale += item['total_sale']
                    r_item['total_sale'] = total_sale
                    total_cost = r_item['total_cost']
                    total_cost += item['total_cost']
                    r_item['total_cost'] = total_cost
            if check == False :
                item['all_group_cost'] = all_group_cost
                result.append( item )
        return result
    
    
    def get_pdtgrp_vals(self):
        res = []
        all_group_cost = 0.0
        disc =abs(self.sp_disc_percentage)
        for line in self.mat_main_pro_line:
            res.append({'pdt_grp_id':line.part_no and line.part_no.od_pdt_group_id and line.part_no.od_pdt_group_id.id,
                'total_sale':line.line_price,
              
                'total_cost': line.line_cost_local_currency,
                })
            all_group_cost += line.line_cost_local_currency
        for line in self.trn_customer_training_line:
            res.append({'pdt_grp_id':line.part_no and line.part_no.od_pdt_group_id and line.part_no.od_pdt_group_id.id,
                'total_sale':line.line_price,
                'total_cost': line.line_cost_local_currency,
                })
            all_group_cost += line.line_cost_local_currency
            
        result = self.grouped_prdgrp_weight(res,all_group_cost)
        for val in result:
            val['disc'] = disc
            sale = val.get('total_sale')
            sal_aftr_disc = sale * (1-(disc/100.0))
            val['sale_aftr_disc'] =sal_aftr_disc
        return result
    
    
    @api.one
    def generate_group_weight(self):
        vals = self.get_pdtgrp_vals()
        self.mat_group_weight_line.unlink()
        self.mat_group_weight_line = vals
    
    
    def get_imp_vals(self):
        result = []
        if (self.bim_tot_sale1 != 0.0 or self.bim_tot_cost1 != 0.0):
            result.append({'sale':self.bim_tot_sale1,'cost':self.bim_tot_cost1,'profit':self.bim_profit1,'tab':'bim'})
        if (self.oim_tot_sale1 != 0.0 or self.oim_tot_cost1 != 0.0):
            result.append({'sale':self.oim_tot_sale1,'cost':self.oim_tot_cost1,'profit':self.oim_profit1,'tab':'oim'})
        return result
    
    def get_amc_vals(self):
        result = []
        if (self.bmn_tot_sale1 != 0.0 or self.bmn_tot_cost1 != 0.0):
            result.append({'sale':self.bmn_tot_sale1,'cost':self.bmn_tot_cost1,'profit':self.bmn_profit1,'tab':'bmn'})
        if (self.omn_tot_sale1 != 0.0 or self.omn_tot_cost1 != 0.0):
            result.append({'sale':self.omn_tot_sale1,'cost':self.omn_tot_cost1,'profit':self.omn_profit1,'tab':'omn'})
        return result
    
    def get_om_vals(self):
        result = []
        if (self.o_m_tot_sale1 != 0.0 or self.o_m_tot_cost1 != 0.0):
            result.append({'sale':self.o_m_tot_sale1,'cost':self.o_m_tot_cost1,'profit':self.o_m_profit1,'tab':'om'})
        
        return result
    
    def get_extra_vals(self):
        result = []
        sale = cost = 0.0
        for line in self.mat_extra_expense_line:
            sale += line.line_price2
            cost += line.line_cost_local
        
        
        if sale or cost:
            result.append({'sale':sale,'cost':cost,'profit':sale-cost,'tab':'mat' })
        sale = cost = 0.0
        for line in self.trn_customer_training_extra_expense_line:
            sale += line.line_price2
            cost += line.line_cost_local
        if sale or cost:
            result.append({'sale':sale,'cost':cost,'profit':sale-cost,'tab':'trn' })
        
        
        return result

    def generate_impl_weight(self):
        res = []
        vals = self.get_pdtgrp_vals()
        imp_vals = self.get_imp_vals()
        disc =  abs(self.sp_disc_percentage)
        for imp_val in imp_vals:
            tab = imp_val.get('tab')
            sale = imp_val.get('sale')
            cost = imp_val.get('cost')
            profit = imp_val.get('profit')
            for val in vals:
                weight = val.get('total_cost')/(val.get('all_group_cost',1.0) or 1.0)
                pdt_grp_id = val.get('pdt_grp_id')
                total_sale = sale * weight 
                total_cost =  cost * weight 
                
                sale_aftr_disc = total_sale * (1-(disc/100.0))
                total_profit = (sale_aftr_disc - total_cost) 
                res.append({'pdt_grp_id':pdt_grp_id,
                            'tab':tab,
                            'total_sale':total_sale,
                            'disc':disc,
                            'sale_aftr_disc': sale_aftr_disc,
                            'total_cost':total_cost,
                            'profit':total_profit})
            
        self.imp_weight_line.unlink()
        self.imp_weight_line = res
    
    def generate_amc_weight(self):
        res = []
        vals = self.get_pdtgrp_vals()
        imp_vals = self.get_amc_vals()
        disc = abs(self.sp_disc_percentage)
        for imp_val in imp_vals:
            tab = imp_val.get('tab')
            sale = imp_val.get('sale')
            cost = imp_val.get('cost')
            profit = imp_val.get('profit')
            for val in vals:
                weight = val.get('total_cost')/(val.get('all_group_cost',1.0) or 1.0)
                pdt_grp_id = val.get('pdt_grp_id')
                total_sale = sale * weight 
                total_cost =  cost * weight 
                sale_aftr_disc = total_sale * (1-(disc/100.0))
                total_profit = (sale_aftr_disc - total_cost) 
                res.append({'pdt_grp_id':pdt_grp_id,
                            'tab':tab,
                            'total_sale':total_sale,
                            'disc':disc,
                            'sale_aftr_disc': sale_aftr_disc,
                            'total_cost':total_cost,
                            'profit':total_profit})
            
        self.amc_weight_line.unlink()
        self.amc_weight_line = res
    
    def generate_om_weight(self):
        res = []
        vals = self.get_pdtgrp_vals()
        imp_vals = self.get_om_vals()
        disc = abs(self.sp_disc_percentage)
        for imp_val in imp_vals:
            tab = imp_val.get('tab')
            sale = imp_val.get('sale')
            cost = imp_val.get('cost')
            profit = imp_val.get('profit')
            for val in vals:
                weight = val.get('total_cost')/(val.get('all_group_cost',1.0) or 1.0)
                pdt_grp_id = val.get('pdt_grp_id')
                total_sale = sale * weight 
                total_cost =  cost * weight 
                sale_aftr_disc = total_sale * (1-(disc/100.0))
                total_profit = (sale_aftr_disc - total_cost) 
                res.append({'pdt_grp_id':pdt_grp_id,
                            'tab':tab,
                            'total_sale':total_sale,
                            'disc':disc,
                            'sale_aftr_disc': sale_aftr_disc,
                            'total_cost':total_cost,
                            'profit':total_profit})
            
        self.om_weight_line.unlink()
        self.om_weight_line = res
        
    
    def generate_extra_weight(self):
        res = []
        vals = self.get_pdtgrp_vals()
        imp_vals = self.get_extra_vals()
        disc = abs(self.sp_disc_percentage)
        for imp_val in imp_vals:
            tab = imp_val.get('tab')
            sale = imp_val.get('sale')
            cost = imp_val.get('cost')
            profit = imp_val.get('profit')
            for val in vals:
                weight = val.get('total_cost')/(val.get('all_group_cost',1.0) or 1.0)
                pdt_grp_id = val.get('pdt_grp_id')
                total_sale = sale * weight 
                total_cost =  cost * weight 
                sale_aftr_disc = total_sale * (1-(disc/100.0))
                total_profit = (sale_aftr_disc - total_cost) 
                
                res.append({'pdt_grp_id':pdt_grp_id,
                            'tab':tab,
                            'total_sale':total_sale,
                             'disc':disc,
                            'sale_aftr_disc': sale_aftr_disc,
                            'total_cost':total_cost,
                            'profit':total_profit})
            
        self.extra_weight_line.unlink()
        self.extra_weight_line = res




    def od_get_company_id(self):
        return self.env.user.company_id

    def default_dead_line_data(self):
        line = [
            {'deadline_type':"mat"},
            {'deadline_type':"project_start"},
            {'deadline_type':"project_close"},
            {'deadline_type':"maint_start"},
            {'deadline_type':"maint_close"},
            {'deadline_type':"availability"},
            {'deadline_type':"start"},
        ]
        return line
    
    def default_payement_term_data(self):
        line = [
            {'payment_name':"Advanced Payement with PO",'payment_percentage':'100%'},
           
        ]
        return line

    @api.one
    def btn_freeze(self):
        self.update_cost_sheet()
        self.freeze = True

    @api.one
    def btn_unfreeze(self):

        self.freeze = False
        self.update_cost_sheet()

    @api.one
    def copy_from_mat(self):
        for line in self.mat_copy_cost_sheet_id.mat_main_pro_line:
            line.copy({'cost_sheet_id':self.id,'group':False,'section_id':False})
    @api.one
    def copy_from_opt(self):
        for line in self.opt_copy_cost_sheet_id.mat_optional_item_line:
            line.copy({'cost_sheet_id':self.id,'group_id':False,'section_id':False})

    @api.one
    def copy_from_trn(self):
        for line in self.trn_copy_cost_sheet_id.trn_customer_training_line:
            line.copy({'cost_sheet_id':self.id,'group':False,'section_id':False,})

    @api.one
    def copy_from_bmn_spare_parts(self):
        for line in self.bmn_copy_spareparts_cs_id.bmn_spareparts_beta_it_maintenance_line:
            line.copy({'cost_sheet_id':self.id,'group':False,'section_id':False,})

    @api.one
    def copy_from_bmn_eqpcoverd(self):
        for line in self.bmn_copy_eqpcoverd_cs_id.bmn_eqp_cov_line:
            line.copy({'cost_sheet_id':self.id})

    @api.one
    def copy_from_omn_spare_parts(self):
        for line in self.omn_copy_spareparts_cs_id.omn_spare_parts_line:
            line.copy({'cost_sheet_id':self.id,'group':False,'section_id':False,})

    @api.one
    def copy_from_omn_eqpcoverd(self):
        for line in self.omn_copy_spareparts_cs_id.omn_eqp_cov_line:
            line.copy({'cost_sheet_id':self.id})
    @api.one
    def copy_from_om_required_parts(self):
        for line in self.om_copy_eqp_required_cs_id.om_eqpmentreq_line:
            line.copy({'cost_sheet_id':self.id,'group':False,'section_id':False,})

    @api.one
    def copy_from_om_eqpcoverd(self):
        for line in self.om_copy_eqpcoverd_cs_id.o_m_eqp_cov_line:
            line.copy({'cost_sheet_id':self.id})

    @api.multi
    def quick_create_analytic(self):
        template_id = False
        if self.is_saudi_comp():
            template_id = 2451
        else:
            template_id = 2449
        owner_id = self.reviewed_id and self.reviewed_id.id or False
        type = 'contract'
        date = self.project_closing_date
        account_manager = self.sales_acc_manager and self.sales_acc_manager.id
        partner_id = self.od_customer_id and self.od_customer_id.id
        ctx = {'default_type':type,'default_od_owner_id':owner_id,'default_template_id':template_id,'default_date':date,
        'default_manager_id':account_manager,'partner_id':partner_id
        }
        return {
                    'view_type': 'form',
                    "view_mode": 'form',
                    'res_model': 'account.analytic.account',
                    'type': 'ir.actions.act_window',
                    'target':'new',
                    'context':ctx,
                    'flags': {'form': {'action_buttons': True}}
            }


    @api.one
    @api.depends('po_date')
    def get_po_date(self):
        self.po_date_kpi = self.po_date

    @api.one
    @api.depends('submitted_date','financial_proposal_date')
    def get_presale_kpi(self):
        submitted_date = self.submitted_date
        financial_proposal_date = self.financial_proposal_date
        if not financial_proposal_date:
            self.presale_kpi = 'not_available'
        else:
            if submitted_date > financial_proposal_date[:10]:
                self.presale_kpi = 'not_ok'
            else:
                self.presale_kpi = "ok"

    def days_between(self,date1, date2):
        d1 = datetime.strptime(date1, "%Y-%m-%d")
        d2 = datetime.strptime(date2, "%Y-%m-%d")
        return (d2 - d1).days
    @api.one
    @api.depends('po_date','handover_date')
    def get_sales_kpi(self):
        po_date = self.po_date
        handover_date = self.handover_date
        if not (handover_date and po_date):
            self.sales_kpi = 'not_available'
        else:
            handover_date = handover_date[:10]
            days = self.days_between(po_date,handover_date)
            if days >3:
                self.sales_kpi = 'not_ok'
            else:
                self.sales_kpi = 'ok'
    @api.one
    @api.depends('processed_date','handover_date')
    def get_owner_kpi(self):
        process_date = self.processed_date
        handover_date = self.handover_date
        if not (handover_date and process_date):
            self.owner_kpi = 'not_available'
        else:
            handover_date = handover_date[:10]
            process_date  = process_date[:10]
            days = self.days_between(handover_date,process_date)
            if days >5:
                self.owner_kpi = 'not_ok'
            else:
                self.owner_kpi = 'ok'
    @api.one
    @api.depends('processed_date','approved_date')
    def get_finance_kpi(self):
        process_date = self.processed_date
        approved_date = self.approved_date
        if not (process_date and approved_date):
            self.finance_kpi = 'not_available'
        else:
            process_date = process_date[:10]
            approved_date  = approved_date[:10]
            days = self.days_between(process_date,approved_date)
            if days >2:
                self.finance_kpi = 'not_ok'
            else:
                self.finance_kpi = 'ok'
    def default_material_summary(self):
        res = """
        <h5 style="color: blue; text-align: center;"><strong><span>Material&nbsp;-&nbsp;المواد</span></strong></h5>
<h5 style="text-align: left;">Covers all types of Material, in case requested in this proposal, such as: Hardware, Software, Warranty, Subscriptions, Licenses, &amp; Training Centers</h5>
<h5 style="text-align: right;">تغطي كل أنواع المواد، في حال طلبها في هذا العرض، وهي على سبيل المثال: القطع، البرمجيات، الضمان، الاشتراكات، الرخص، والتدريب في المراكز</h5>
        """
        return res
    def default_implementation_summary(self):
        res = """
        <h5 style="color: blue; text-align: center;"><span><strong>Implementation -&nbsp;خدمات التركيب</strong></span></h5>
<h5 style="text-align: left;">Implementation &amp; Configuration Services for Devices &amp; Systems</h5>
<h5 style="text-align: right;">الخدمة الفنية للتركيب والتعريف للأجهزة والأنظمة</h5>
        """
        return res
    def default_amc_summary(self):
        res = """
        <h5 style="color: blue; text-align: center;"><strong><span>Maintenance -&nbsp;الصيانة</span></strong></h5>
<h5 style="text-align: left;">Maintenance Services (Such as Preventive Maintenance, Remedial Maintenance, etc.). These services do not include manufacturer warranty or subscriptions. Refer to Material Section for warranty and subscription.</h5>
<h5 style="direction: rtl; text-align: right;">خدمة الصيانة (كالصيانة الوقائية الدورية، أو إصلاح المشاكل، أو غيرها). لا تشمل هذه الخدمة الضمان أو الاشتراكات المقدمة من قبل طرف الشركة المصنعة. يرجى الرجوع إلى قسم الضمان أوالاشتراكات في المواد</h5>
        """
        return res
    def default_operation_summary(self):

        res = """
        <h5 style="color: blue; text-align: center;"><strong><span>Operation -&nbsp;التشغيل</span></strong></h5>
<h5 style="text-align: left;">O&amp;M Service for Resident Engineers / Employees at Customer Site</h5>
<h5 style="direction: rtl; text-align: right;">خدمات التشغيل بواسطة مهندسين / موظفين مقيمين لدى العميل</h5>
        """
        return res

    @api.onchange('mat_select_all')
    def onchange_check_all(self):
		if self.mat_select_all:
			for x in self.mat_main_pro_line:
				x.check = True
		else:
			for x in self.mat_main_pro_line:
				x.check = False

    def gen_line_check(self,trg,line_id):
        if trg:
            for x in line_id:
                x.check = True
        else:
            for x in line_id:
                x.check = False

    @api.onchange('mat_opt_select_all')
    def onchange_mat_check_all(self):
        self.gen_line_check(self.mat_opt_select_all,self.mat_optional_item_line)

    @api.onchange('mat_ext_sel')
    def onchange_mat_ext_check_all(self):
        self.gen_line_check(self.mat_ext_sel,self.mat_extra_expense_line)

    @api.onchange('ren_main_select')
    def onchange_ren_main_check_all(self):
        self.gen_line_check(self.ren_main_select,self.ren_main_pro_line)

    @api.onchange('ren_opt_select')
    def onchange_ren_opt_check_all(self):
        self.gen_line_check(self.ren_opt_select,self.ren_optional_item_line)

    @api.onchange('trn_sel')
    def onchange_trn_check_all(self):
        self.gen_line_check(self.trn_sel,self.trn_customer_training_line)

    @api.onchange('trn_ext_sel')
    def onchange_trn_ext_check_all(self):
        self.gen_line_check(self.trn_ext_sel,self.trn_customer_training_extra_expense_line)

    @api.one
    def delete_mat_line(self):
        for line in self.mat_main_pro_line:
            if line.check:
                line.unlink()

    def delete_general_line(self,line_id):
        for line in line_id:
            if line.check:
                line.unlink()

    @api.one 
    def btn_del_mat_opt_line(self):
        self.delete_general_line(self.mat_optional_item_line)

    @api.one 
    def btn_del_mat_ext_line(self):
        self.delete_general_line(self.mat_extra_expense_line)

    @api.one 
    def btn_del_ren_main_line(self):
        self.delete_general_line(self.ren_main_pro_line)


    @api.one 
    def btn_del_ren_opt_line(self):
        self.delete_general_line(self.ren_optional_item_line)

    @api.one 
    def btn_del_trn_line(self):
        self.delete_general_line(self.trn_customer_training_line)

    @api.one 
    def btn_del_trn_ext_line(self):
        self.delete_general_line(self.trn_customer_training_extra_expense_line)

    

    mat_select_all = fields.Boolean(string="Select All")
    mat_opt_select_all = fields.Boolean(string="Select All")
    mat_ext_sel = fields.Boolean(string="Select All")

    ren_main_select = fields.Boolean(string="Select All")
    ren_opt_select = fields.Boolean(string="Select All")

    trn_sel = fields.Boolean(string="Select All")
    trn_ext_sel = fields.Boolean(string="Select All")

    bim_sel = fields.Boolean(string="Select All")

    
    od_cost_centre_id =fields.Many2one('od.cost.centre',string='Cost Centre')
    od_branch_id =fields.Many2one('od.cost.branch',string='Branch')
    od_division_id =fields.Many2one('od.cost.division',string='Division')
    sale_team_id = fields.Many2one('crm.case.section',string="Sale Team",related="lead_id.section_id",readonly=True)
    op_stage_id = fields.Many2one('crm.case.stage',string="Opp Stage",related="lead_id.stage_id",readonly=True)    
    op_expected_booking = fields.Date(string="Opp Expected Booking",related="lead_id.date_action",readonly=True,store=True)    
   
    material_summary = fields.Html(string="Material Summary",default=default_material_summary)
    implementation_summary = fields.Html(string="Implementation Summary",default=default_implementation_summary)
    amc_summary = fields.Html(string="Amc Summary",default=default_amc_summary)
    operation_summary = fields.Html(string="Operation Summary",default=default_operation_summary)
    od_timesheet_amount = fields.Float(string="Timesheet Amount",compute="od_get_timesheet_amount")
    od_journal_amount = fields.Float(string="Journal Amount",compute="od_get_lead_journal_amount")
    finance_kpi = fields.Selection([('ok','OK'),('not_ok','Not Ok!!!'),('not_available','Not Available')],string="Finance KPI",compute="get_finance_kpi")
    ignore_vat =fields.Boolean(string="Ignore VAT")
    owner_kpi = fields.Selection([('ok','OK'),('not_ok','Not Ok!!!'),('not_available','Not Available')],string="Owner KPI",compute="get_owner_kpi")
    sales_kpi = fields.Selection([('ok','OK'),('not_ok','Not Ok!!!'),('not_available','Not Available')],string="Sales KPI",compute="get_sales_kpi")
    presale_kpi = fields.Selection([('ok','OK'),('not_ok','Not Ok!!!'),('not_available','Not Available')],string="Presale KPI",compute="get_presale_kpi")
    name = fields.Char(string='Name',required=True,track_visibility='always')
    project_closing_date = fields.Date(string="Project Closing Date")
    od_hr_claim_amount = fields.Float(string="Hr Exp Claim Amount",compute="od_get_hr_exp_claim_amount")
    saved = fields.Boolean(string='Saved')
    freeze = fields.Boolean(string="Freezed Unit Price")
    mat_copy_cost_sheet_id = fields.Many2one('od.cost.sheet',string="Material Copy Sheet",states={'draft':[('readonly',False)]},readonly=True)
    opt_copy_cost_sheet_id = fields.Many2one('od.cost.sheet',string="Optional Copy Sheet",states={'draft':[('readonly',False)]},readonly=True)
    trn_copy_cost_sheet_id = fields.Many2one('od.cost.sheet',string="Training Copy Sheet",states={'draft':[('readonly',False)]},readonly=True)
    bmn_copy_spareparts_cs_id = fields.Many2one('od.cost.sheet',string="Bmn Spare Parts Copy Sheet",states={'draft':[('readonly',False)]},readonly=True)
    bmn_copy_eqpcoverd_cs_id = fields.Many2one('od.cost.sheet',string="Bmn Eqpment Covered Cost Sheet",states={'draft':[('readonly',False)]},readonly=True)
    omn_copy_spareparts_cs_id = fields.Many2one('od.cost.sheet',string="Omn Spare Parts Copy Sheet",states={'draft':[('readonly',False)]},readonly=True)
    omn_copy_eqpcoverd_cs_id = fields.Many2one('od.cost.sheet',string="Omn Eqpment Covered Cost Sheet",states={'draft':[('readonly',False)]},readonly=True)
    om_copy_eqp_required_cs_id = fields.Many2one('od.cost.sheet',string="OM Eqpment Required Cost Sheet",states={'draft':[('readonly',False)]},readonly=True)
    om_copy_eqpcoverd_cs_id = fields.Many2one('od.cost.sheet',string="OM Eqpment Covered Cost Sheet",states={'draft':[('readonly',False)]},readonly=True)

    od_version = fields.Char(string="Version",states={'draft':[('readonly',False)],'submitted':[('readonly',False)],'design_ready':[('readonly',False)],'returned_by_pmo':[('readonly',False)]},readonly=True)
    project_manager = fields.Many2one('res.users','Project Manager',states={'submitted':[('readonly',False)],'design_ready':[('readonly',False)],'returned_by_pmo':[('readonly',False)]},readonly=True,track_visibility='always')
    support_doc_line = fields.One2many('od.support.doc.line','cost_sheet_id',string='Support Doc Lin',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'analytic_change':[('readonly',False)]},readonly=True)
    deadlines = fields.One2many('od.deadlines','cost_sheet_id',string='Deadlines',copy=True,default=default_dead_line_data,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'processed':[('readonly',False)],'analytic_change':[('readonly',False)]},readonly=True)
    payment_schedule_line = fields.One2many('od.payment.schedule','cost_sheet_id',string='Payment Schedule',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'processed':[('readonly',False)],'analytic_change':[('readonly',False)],'change':[('readonly',False)]},readonly=True)
    comm_matrix_line = fields.One2many('od.comm.matrix','cost_sheet_id',string='Communication Matrix',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'processed':[('readonly',False)],'change':[('readonly',False)],'analytic_change':[('readonly',False)]},readonly=True)
    date_log_history_line = fields.One2many('od.date.log.history','cost_sheet_id',strint="Date Log History",readonly=True,copy=False)
    change_management_line = fields.One2many('change.management','cost_sheet_id',strint="Change Request",readonly=True,copy=False)
    sale_order_original_line = fields.One2many('sale.order','od_cost_sheet_id',strint="Original",readonly=True,copy=False)
    
    bid_bond_submit = fields.Selection([('yes','Yes'),('no','No')],'Bid Bond Submit')
    peromance_bond = fields.Selection([('yes','Yes'),('no','No')],'Perfomance Bond')
    penalty_clause = fields.Selection([('yes','Yes'),('no','No')],'Penalty Clause')
    insurance_req = fields.Selection([('yes','Yes'),('no','No')],'Insurance Required')
    po_status = fields.Selection([('waiting_po','Waiting P.O'),('special_approval','Special Approval From GM'),('available','Available')],'Customer PO Status')
    adv_payment_status = fields.Selection([('not_required','Not Required'),('required','Required,Not Paid'),('paid','Paid'),('gm',' Waived by G.M.')],'Advance Payment Status')

    po_date = fields.Date("Customer PO Date")
    po_date_kpi = fields.Date("PO Date",compute="get_po_date")

    bid_bond_rev_comment_id = fields.Many2one('od.reviewer.comment',string="Bid Bond Reviewer Comment")
    perfomance_rev_comment_id = fields.Many2one('od.reviewer.comment',string="Perfomance Bond Reviewer Comment")
    penalty_rev_comment_id = fields.Many2one('od.reviewer.comment',string="Penalty Clause Reviewer Comment")
    insurance_rev_comment_id = fields.Many2one('od.reviewer.comment',string="Insurance Reviewer Comment")
    po_status_rev_comment_id = fields.Many2one('od.reviewer.comment',string="PO Status Reviewer Comment")
    po_date_rev_comment_id = fields.Many2one('od.reviewer.comment',string="PO Date Reviewer Comment")
    adv_payment_rev_comment_id = fields.Many2one('od.reviewer.comment',string="Advance Payment Reviewer Comment")

    bid_bond_fin_comment_id = fields.Many2one('od.finance.comment',string="Bid Bond Finance Comment")
    perfomance_fin_comment_id = fields.Many2one('od.finance.comment',string="Perfomance Bond Finance Comment")
    penalty_fin_comment_id = fields.Many2one('od.finance.comment',string="Penalty Clause Finance Comment")
    insurance_fin_comment_id = fields.Many2one('od.finance.comment',string="Insurance Finance Comment")
    po_status_fin_comment_id = fields.Many2one('od.finance.comment',string="PO Status Finance Comment")
    po_date_fin_comment_id = fields.Many2one('od.finance.comment',string="PO Date Finance Comment")
    adv_payment_fin_comment_id = fields.Many2one('od.finance.comment',string="Advance Payment Finance Comment")

    project_closing_fin_comment_id = fields.Many2one('od.finance.comment',string="Project Closing Finance Comment")
    customer_reg_id = fields.Many2one('od.customer.reg',string='Customer Registration')
    handover_reviewer = fields.Many2one('res.users','Projects / Service Desk Review')
    finance_reviewer = fields.Many2one('res.users','Finance Review')
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    submitted_date = fields.Datetime('Design Ready Date',readonly=True)
    submit_to_customer_date = fields.Datetime("Submit To Customer Date")
    handover_date = fields.Datetime('Hand-Over Date',readonly=True)
    processed_date = fields.Datetime('Processed Date',readonly=True)
    approved_date = fields.Datetime('Approved Date',readonly=False)
    #hand over tab
    sales_acc_manager = fields.Many2one('res.users',string='Sales Account Manager')
    business_development = fields.Many2one('res.users',string='Business Development')
    pre_sales_engineer = fields.Many2one('res.users',string='Pre-Sales Engineer')
    technical_consultant1 = fields.Many2one('res.users',string='Technical Consultant 1')
    technical_consultant2 = fields.Many2one('res.users',string='Technical Consultant 2')
    accountant = fields.Many2one('res.users',string='Accountant')
    sales_order_generated = fields.Boolean(string="Sales Order Generated",default=False,copy=False)
   
    @api.onchange('approved_date')
    def onchange_approved(self):
        approved_date = self.approved_date
        if approved_date:
            expected_booking= approved_date[:10]
            self.lead_id.write({'date_action':expected_booking})
    
    @api.one
    def check_payment_term(self):
        if not self.payment_terms_line:
            raise Warning("Enter Payment Terms")

    @api.one 
    def double_check_vat(self):
        vat = .05
        check_vat_amount =self.sum_total_sale * vat 
        vat_amount = self.sum_vat
        if not self.ignore_vat and abs(vat_amount -check_vat_amount) >1:
            raise Warning("Please Double Check the VAT Amount")
    
    def print_cost_sheet(self, cr, uid, ids, context=None):
        self.update_cost_sheet(cr,uid,ids,context=context)
        self.double_check_vat(cr,uid,ids,context=context)
#         self.check_payment_term(cr,uid,ids,context=context)
        return self.pool['report'].get_action(cr, uid, ids, 'report.Beta_IT_Proposal', context=context)


    def get_saudi_company_id(self):
        parameter_obj = self.env['ir.config_parameter']
        key =[('key', '=', 'od_beta_saudi_co')]
        company_param = parameter_obj.search(key)
        if not company_param:
            raise Warning(_('Settings Warning!'),_('No Company Parameter Not defined\nconfig it in System Parameters with od_beta_saudi_co!'))
        saudi_company_id = company_param.od_model_id and company_param.od_model_id.id or False
        return saudi_company_id

    def check_reviewer_comment(self,line_ids,detail):
        for line in line_ids:
            if line.rev_comment_id.id == False:
                raise Warning('Reviewer Comment Blank In Handover %s Record' %detail)

    def check_payment_schedule(self):
        for line in self.payment_schedule_line:
            if not line.milestone:
                raise Warning('Link To Milestone Missing in Handover Payment Schedule Record')
    def check_rev_exist(self):
        # self.check_reviewer_comment(self.support_doc_line, 'Supporting Documents')
        self.check_reviewer_comment(self.deadlines, 'Deadlines')
        self.check_reviewer_comment(self.comm_matrix_line, 'Communication Matrix Line')
        self.check_payment_schedule()
    def check_proof_cost(self):
        for line in self.costgroup_material_line:
            if not line.proof_of_cost:
                return True
        for line in self.costgroup_optional_line:
            if not line.proof_of_cost:
                return True
        for line in self.costgroup_it_service_line:
            if not line.proof_of_cost:
                return True
        return False

    def check_handover_min_docs(self):
        # if len(self.support_doc_line) < 1:
        #     raise Warning('At least One  Supporting Doc Line Required')
        if len(self.deadlines) <1 :
            raise Warning('At least One  Deadlines Record Required')
        if len(self.payment_schedule_line) <1 :
            raise Warning('At least One  Payment Schedule Line is Required')
        if len(self.comm_matrix_line) <1 :
            raise Warning('At least One  Communication Matrix Line is Required')
        for line in self.comm_matrix_line:
            if line.partner_id.id == False :
                raise Warning('At least One Customer Required in Matrix line')
            if line.customer_role_id.id == False:
                raise Warning('At least One Customer Role  Required in Matrix line')
        if not self.bid_bond_submit:
            raise Warning('All General Questionnaire Should Be Answered')
        if not self.peromance_bond:
            raise Warning('All General Questionnaire Should Be Answered')
        if not self.customer_reg_id:
            raise Warning('All General Questionnaire Should Be Answered')
        if not self.penalty_clause:
            raise Warning('All General Questionnaire Should Be Answered')


    def check_process_min_docs(self):
        # if len(self.customer_closing_line) < 1:
        #     raise Warning('At least One  Customer Closing Line Record Required')
        # if len(self.beta_closing_line) <1:
        #     raise Warning('At least One  Beta Closing Condition Record Required')
        if not self.project_closing_date:
            raise Warning("Project Closing Date Not Set")
        if not self.bid_bond_rev_comment_id:
            raise Warning("Bid Bond Reviewer Comment is not Set")
        if not self.perfomance_rev_comment_id:
            raise Warning("Perfomance Bond Reviewer Comment not Set")
        if not self.insurance_rev_comment_id:
            raise Warning("Penalty Close Reviewer Comment not Set")
        if not self.penalty_rev_comment_id:
            raise Warning("insurance Reviewer Comment Not set")
        if not self.po_status_rev_comment_id:
            raise Warning("Customer PO Status Reviewer Comment Not Set")
        if not self.closing_condition_ids:
            raise Warning("Update Closing Condition")
    def common_check_fin(self,line_id,label):
        for line in line_id:
            if not line.fin_comment_id.id:
                raise Warning("%s Finance Comment Is Blank"%label)

    def check_finance_comment(self):
        # self.common_check_fin(self.support_doc_line,"Supporting Documents")
        self.common_check_fin(self.deadlines,"Deadlines Documents")
        self.common_check_fin(self.payment_schedule_line,"Payment Schedule Documents")
        self.common_check_fin(self.comm_matrix_line,"Communication Matrix Documents")
        # self.common_check_fin(self.customer_closing_line,"Customer Closing Line Documents")
        # self.common_check_fin(self.beta_closing_line,"Beta IT Closing Condition Line Documents")
        if not self.closing_fin_comment_id:
            raise Warning("Finance Comment Needed in Closing Condition")
        if not self.project_closing_fin_comment_id:
            raise Warning("Finance Comment Needed in Project Closing Date")
        if not self.bid_bond_fin_comment_id:
            raise Warning("Bid Bond Finance Comment is not Set")
        if not self.perfomance_fin_comment_id:
            raise Warning("Perfomance Bond Finance Comment not Set")
        if not self.insurance_fin_comment_id:
            raise Warning("Penalty Close Finance Comment not Set")
        if not self.penalty_fin_comment_id:
            raise Warning("insurance Finance Comment Not set")
        if not self.po_status_fin_comment_id:
            raise Warning("Customer PO Status Finance Comment Not set")

    def od_send_mail(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        saudi_comp =self.get_saudi_company_id()
        if self.company_id.id == saudi_comp:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference('orchid_cost_sheet', template)[1]
        print "template id>>>>>>>>>>>>>>>",template_id
        cost_sheet_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,cost_sheet_id, force_send=True)
        return True

    def od_open_attachement(self,cr,uid,ids,context=None):

        model_name=self._name
        object_id = ids[0]
        domain = [('model_name','=',model_name),('object_id','=',object_id)]
        ctx = {'default_model_name':model_name,'default_object_id':object_id,'default_costsheet_doc':True}
        return {
            'domain': domain,
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'od.attachement',
            'type': 'ir.actions.act_window',
            'context':ctx
                }
    @api.one
    def _od_attachement_count(self):
        for obj in self:
            attachement_ids = self.env['od.attachement'].search([('model_name', '=', self._name),('object_id','=',obj.id)])
            if attachement_ids:
                self.od_attachement_count = len(attachement_ids)


    @api.one 
    @api.onchange('bim_log_group')
    def onchngage_bim_log_group(self):
        self.bim_tax_id = self.bim_log_group and self.bim_log_group.tax_id and self.bim_log_group.tax_id.id or False
    
    @api.one
    @api.depends('bim_log_cost','bim_log_group')
    def compute_bim_log_price(self):
        if self.bim_log_group:
            group = self.bim_log_group
            profit = group.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%group.name)
            discount = group.customer_discount/100
            unit_cost = self.bim_log_cost
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.bim_log_price = unit_price



    def set_trn_cost_group(self,res):
        costgroup_material_pool = self.env['od.cost.costgroup.material.line']
        for data in res:
            sheet_id = data.id
            for line in data.trn_customer_training_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_material_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_trn_section(self,res):
        section_pool = self.env['od.cost.trn.section.line']
        for data in res:
            sheet_id = data.id
            for line in data.trn_customer_training_line:
                section_name = line.trn_section_id and line.trn_section_id.section or ''
                sections = section_pool.search([('cost_sheet_id','=',sheet_id),('section','=',section_name)])
                if len(sections)  == 1:
                    line['trn_section_id'] = sections.id
                else:
                    line['trn_section_id'] = False
    def set_trn_extra_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.extra.expense.line']
        for data in res:
            sheet_id = data.id
            for line in data.trn_customer_training_extra_expense_line:
                group_name = line.group2 and line.group2.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group2'] = cst_grops.id
                else:
                    line['group2'] = False

    def set_mat_cost_group(self,res):
        costgroup_material_pool = self.env['od.cost.costgroup.material.line']
        for data in res:
            sheet_id = data.id
            for line in data.mat_main_pro_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_material_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_mat_section(self,res):
        section_pool = self.env['od.cost.section.line']
        for data in res:
            sheet_id = data.id
            for line in data.mat_main_pro_line:
                section_name = line.section_id and line.section_id.section or ''
                sections = section_pool.search([('cost_sheet_id','=',sheet_id),('section','=',section_name)])
                if len(sections)  == 1:
                    line['section_id'] = sections.id
                else:
                    line['section_id'] = False

    def set_opt_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.optional.line.two']
        for data in res:
            sheet_id = data.id
            for line in data.mat_optional_item_line:
                group_name = line.group_id and line.group_id.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group_id'] = cst_grops.id
                else:
                    line['group_id'] = False

    def set_opt_section(self,res):
        section_pool = self.env['od.cost.opt.section.line']
        for data in res:
            sheet_id = data.id
            for line in data.mat_optional_item_line:
                section_name = line.opt_section_id and line.opt_section_id.section or ''
                sections = section_pool.search([('cost_sheet_id','=',sheet_id),('section','=',section_name)])
                if len(sections)  == 1:
                    line['opt_section_id'] = sections.id
                else:
                    line['opt_section_id'] = False
    def set_mat_extra_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.extra.expense.line']
        for data in res:
            sheet_id = data.id
            for line in data.mat_extra_expense_line:
                group_name = line.group2 and line.group2.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group2'] = cst_grops.id
                else:
                    line['group2'] = False

    def set_imp_extra_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.implimentation_extra_expense_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False

    def set_imp_manpower_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.manpower_manual_line:
                group_name = line.cost_group_id and line.cost_group_id.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['cost_group_id'] = cst_grops.id
                else:
                    line['cost_group_id'] = False

    def set_imp_man_imp_code_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.bim_implementation_code_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_oim_price_calculation_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.oim_implimentation_price_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_oim_extra_exp_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.oim_extra_expenses_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_bim_log_group(self,res):
        costgroup_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            group_name = data.bim_log_group and data.bim_log_group.name or ''
            cst_grops = costgroup_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
            if len(cst_grops)  == 1:
                data.bim_log_group = cst_grops.id
            else:
                data.bim_log_group = False
    def set_amc_preventive_mnt_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.bmn_it_preventive_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False

    def set_amc_remedial_mnt_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.bmn_it_remedial_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_amc_spareparts_cost_group(self,res):
        costgroup_material_pool = self.env['od.cost.costgroup.material.line']
        for data in res:
            sheet_id = data.id
            for line in data.bmn_spareparts_beta_it_maintenance_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_material_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_amc_spareparts_section(self,res):
        section_pool = self.env['od.cost.section.line']
        for data in res:
            sheet_id = data.id
            for line in data.bmn_spareparts_beta_it_maintenance_line:
                section_name = line.section_id and line.section_id.section or ''
                sections = section_pool.search([('cost_sheet_id','=',sheet_id),('section','=',section_name)])
                if len(sections)  == 1:
                    line['section_id'] = sections.id
                else:
                    line['section_id'] = False
    def set_amc_bmn_extra_exp_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.bmn_beta_it_maintenance_extra_expense_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_amc_omn_preventive_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.omn_out_preventive_maintenance_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_amc_omn_remedial_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.omn_out_remedial_maintenance_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_amc_omn_spareparts_section(self,res):
        section_pool = self.env['od.cost.section.line']
        for data in res:
            sheet_id = data.id
            for line in data.omn_spare_parts_line:
                section_name = line.section_id and line.section_id.section or ''
                sections = section_pool.search([('cost_sheet_id','=',sheet_id),('section','=',section_name)])
                if len(sections)  == 1:
                    line['section_id'] = sections.id
                else:
                    line['section_id'] = False
    def set_amc_omn_spareparts_cost_group(self,res):
        costgroup_material_pool = self.env['od.cost.costgroup.material.line']
        for data in res:
            sheet_id = data.id
            for line in data.omn_spare_parts_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_material_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_amc_omn_extra_exp_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.omn_maintenance_extra_expense_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_om_resident_eng_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.om_residenteng_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_om_material_section(self,res):
        section_pool = self.env['od.cost.section.line']
        for data in res:
            sheet_id = data.id
            for line in data.om_eqpmentreq_line:
                section_name = line.section_id and line.section_id.section or ''
                sections = section_pool.search([('cost_sheet_id','=',sheet_id),('section','=',section_name)])
                if len(sections)  == 1:
                    line['section_id'] = sections.id
                else:
                    line['section_id'] = False
    def set_om_material_cost_group(self,res):
        costgroup_material_pool = self.env['od.cost.costgroup.material.line']
        for data in res:
            sheet_id = data.id
            for line in data.om_eqpmentreq_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_material_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False
    def set_om_extra_exp_cost_group(self,res):
        costgroup_opt_pool = self.env['od.cost.costgroup.it.service.line']
        for data in res:
            sheet_id = data.id
            for line in data.om_extra_line:
                group_name = line.group and line.group.name or ''
                cst_grops = costgroup_opt_pool.search([('cost_sheet_id','=',sheet_id),('name','=',group_name)])
                if len(cst_grops)  == 1:
                    line['group'] = cst_grops.id
                else:
                    line['group'] = False


    @api.one
    def copy(self,defaults):
        context = self._context
        defaults['name'] = self.name + '[copy]'
        defaults['number'] = self.env['ir.sequence'].get('od.cost.sheet') or '/'
        defaults['status'] = 'revision'
        defaults['sales_order_generated'] = False
        res = super(od_cost_sheet,self).copy(defaults)
        self.set_mat_cost_group(res)
        self.set_opt_cost_group(res)
        self.set_mat_extra_cost_group(res)

        self.set_mat_section(res)
        self.set_opt_section(res)

        self.set_trn_cost_group(res)
        self.set_trn_section(res)
        self.set_trn_extra_cost_group(res)

        self.set_bim_log_group(res)
        self.set_imp_extra_cost_group(res)
        self.set_imp_manpower_cost_group(res)
        self.set_imp_man_imp_code_cost_group(res)
        self.set_oim_price_calculation_cost_group(res)
        self.set_oim_extra_exp_cost_group(res)

        self.set_amc_preventive_mnt_cost_group(res)
        self.set_amc_remedial_mnt_cost_group(res)

        self.set_amc_spareparts_cost_group(res)
        self.set_amc_spareparts_section(res)
        self.set_amc_bmn_extra_exp_cost_group(res)
        self.set_amc_omn_preventive_cost_group(res)
        self.set_amc_omn_remedial_cost_group(res)
        self.set_amc_omn_spareparts_section(res)
        self.set_amc_omn_spareparts_cost_group(res)
        self.set_amc_omn_extra_exp_cost_group(res)

        self.set_om_resident_eng_cost_group(res)
        self.set_om_material_section(res)
        self.set_om_material_cost_group(res)
        self.set_om_extra_exp_cost_group(res)
        return res

           
    def update_opp_stage_design_ready(self):
        
        opp_design_ready_state_id =4
        check_ids = [6,12,5]#won pipeline commit stage ids
        if self.lead_id.stage_id.id not in check_ids:
            self.lead_id.write({'stage_id':opp_design_ready_state_id})
    
    def update_opp_stage_submitted(self):
        pipe_stage_id =12
        check_ids = [1,4] #approved, design ready stage
        if self.lead_id.stage_id.id in check_ids:
            self.lead_id.write({'stage_id':pipe_stage_id})
            
    @api.one 
    def btn_design_ready(self):
        self.update_cost_sheet()
        self.submitted_date = str(datetime.now())
        if self.status == 'active':
            date =str(datetime.now())
            self.lead_id.finished_on_7 =date[:10]
        self.state ='design_ready'
        self.date_log_history_line = [{'name':'Design Ready','date':str(datetime.now())}]
        self.update_opp_stage_design_ready()
        self.od_send_mail('cst_sheet_submit_mail')

        
    
    
    @api.one
    def btn_submit(self):
        self.state ='submitted'
        date_now =str(datetime.now())
        self.submit_to_customer_date = date_now
        self.date_log_history_line = [{'name':'Submit To Customer','date':date_now}]
        self.update_opp_stage_submitted()

    
    
    @api.multi
    def button_cancel(self):
        ctx = {'method':'btn_cancel'}
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'gen.wiz.confirm',
                'context':ctx,
                'type': 'ir.actions.act_window',
                'target': 'new',

            }
    
    @api.one 
    def btn_cancel(self):
        sale_pool = self.env['sale.order']
        so_tab_map,so_analyti_map = self.get_so_tab_map()
        for tab,sale_id in so_tab_map.iteritems():
            if sale_id:
                sale_obj = sale_pool.browse(sale_id)
                sale_state = sale_obj.state
                if sale_state != 'cancel':
                    raise Warning("The Sale Order With ID %s Related Cost Sheet State Must be in the State of Cancel,Please Make the Sale Order to the State Cancel First"%sale_id)
        self.write({'state':'cancel'})

    @api.one
    def btn_reset_draft(self):
        self.state ='draft'
        self.date_log_history_line = [{'name':'Submit to Draft','date':str(datetime.now())}]

    def check_any_tab_include(self):
        tab_include = [self.included_in_quotation,self.included_trn_in_quotation,self.included_bim_in_quotation,self.included_bmn_in_quotation,self.included_om_in_quotation]
        if not any(tab_include) == True:
            return False
        return True
    @api.one
    def btn_handover(self):
        if self.status != 'active':
            raise Warning('Only Active Cost Sheet Can Be Handovered')
        if not self.check_any_tab_include():
            raise Warning("Nothing is Included to Handover")
        if not self.comm_made_to_customer:
            raise Warning("Commitment Made to Customer is Blank")
        if not self.comm_made_to_customer:
            raise Warning("Commitment Made Customer to Me is Blank")

        self.handover_date = str(datetime.now())
        check_proof_cost = self.check_proof_cost()
        if check_proof_cost:
            raise Warning('Proof Of Cost field is Empty,Which Will Not Allow To Handover Cost Sheet!!!!')
        self.check_handover_min_docs()
        self.state ='handover'
        self.date_log_history_line = [{'name':'Handover Date','date':str(datetime.now())}]
        self.od_send_mail('cst_sheet_handover_mail')

    @api.one
    def btn_reset_submit(self):
        self.od_send_mail('cst_sheet_reset_submit_mail')
        self.date_log_history_line = [{'name':'Return By PMO','date':str(datetime.now())}]
        self.state = 'returned_by_pmo'

    @api.one
    def btn_waiting_po(self):
        self.date_log_history_line = [{'name':'Waiting PO','date':str(datetime.now())}]
        self.state = 'waiting_po'

    @api.one
    def btn_waiting_to_handover(self):
        self.date_log_history_line = [{'name':'Waiting to Handover','date':str(datetime.now())}]
        self.state = 'handover'
    @api.one
    def btn_process(self):
        self.check_rev_exist()
        self.processed_date = str(datetime.now())
        self.check_process_min_docs()
        self.od_send_mail('cst_sheet_process_mail')
        self.date_log_history_line = [{'name':'Processed Date','date':str(datetime.now())}]
        self.state = 'processed'
    @api.one
    def btn_reset_handover(self):
        self.od_send_mail('cst_sheet_reset_handover_mail')
        self.date_log_history_line = [{'name':'Return By Finance','date':str(datetime.now())}]
        self.state = 'returned_by_fin'
    
    
    def update_opp_stage(self):
        stage_pool = self.env['crm.case.stage']
        stage_ob = stage_pool.search([('name','=','Won')],limit =1)
        if not stage_ob:
            raise Warning("Won Stage Not Available Please Create One for Opportunity")
        stage_id = stage_ob.id
        self.lead_id.write({'stage_id':stage_id})

    def check_adv_payment(self):
        if self.adv_payment_status == 'required':
            raise Warning("Advance Payment Not Collected Yet")
        return True
    @api.one
    def btn_approved(self):
#         self.od_send_mail('cst_sheet_approve_mail')
# this mail wiil be sent when assign an accountant
        self.check_adv_payment()
        self.check_finance_comment()
#         if not self.approved_date:
#             self.approved_date = str(datetime.now())
        self.date_log_history_line = [{'name':'Button Approved Log Date','date':str(datetime.now())}]
        # self.status = 'baseline'
        self.generate_sale_order()
        self.update_opp_stage()
        # self.state = 'approved'

    @api.one
    def btn_reset_process(self):
        self.state = 'processed'
        self.date_log_history_line = [{'name':'Approved To Process','date':str(datetime.now())}]
        self.od_send_mail('cst_sheet_reset_process_mail')
    @api.one
    def btn_allow_change(self):
        self.sales_order_generated = True
        self.state = 'change'
        self.change_date = str(datetime.now())
        self.date_log_history_line = [{'name':'Allow Change','date':str(datetime.now())}]
#         self.od_send_mail('cst_sheet_allow_change_mail')

    @api.one
    def btn_redistribute_analytic(self):
        self.sales_order_generated = True
        self.state = 'analytic_change'
        self.change_date = str(datetime.now())
        self.date_log_history_line = [{'name':'Redistribute Analytic','date':str(datetime.now())}]

    @api.one
    def btn_modify(self):
        self.sales_order_generated = True
        self.state = 'modify'
        self.change_date = str(datetime.now())
        self.date_log_history_line = [{'name':'Modify','date':str(datetime.now())}]

    
    
    
    def get_imp_cost(self):
        cost =0.0
        
        if self.included_bim_in_quotation:
            cost = sum([x.line_cost for x in self.manpower_manual_line ])
            
            if self.bim_log_select:
                cost += self.bim_log_cost
               
            if self.bim_imp_select:
                cost += sum([x.line_cost for x in self.bim_implementation_code_line])
               
        return cost
    
    def get_bmn_cost(self):
        cost =0.0
        if self.included_bmn_in_quotation:
            cost =sum([x.line_cost for x in self.bmn_it_preventive_line ])+sum([x.line_cost for x in self.bmn_it_remedial_line])
        return cost
    
    def calculate_imp(self):
        sale =cost =profit=profit_per=0.0
        bim_vat  = 0.0
        if self.included_bim_in_quotation:
            cost = sum([x.line_cost for x in self.manpower_manual_line ])
            sale = sum([x.line_price for x in self.manpower_manual_line ])
            bim_vat += self.get_vat_total(self.manpower_manual_line)
            if self.bim_log_select:
                cost += self.bim_log_cost
                sale += self.bim_log_price
                bim_vat += self.bim_log_vat_value
            if self.bim_imp_select:
                cost += sum([x.line_cost for x in self.bim_implementation_code_line])
                sale += sum([x.line_price for x in self.bim_implementation_code_line])
                bim_vat += self.get_vat_total(self.bim_implementation_code_line)
            profit = sale - cost 
            profit_per =0.0 
            if sale:
                profit_per = (profit/sale) * 100
        
        self.a_bim_cost = cost 
        self.a_bim_sale = sale 
        self.a_bim_profit = profit 
        self.a_bim_profit_percentage = profit_per
        self.a_bim_vat = bim_vat
        return {'cost':cost,'sale':sale,'vat':bim_vat}
    def calculate_bmn(self):
        sale =cost =profit=profit_per=bmn_vat =0.0
        if self.included_bmn_in_quotation:
            cost =sum([x.line_cost for x in self.bmn_it_preventive_line ])+sum([x.line_cost for x in self.bmn_it_remedial_line])
            sale =sum([x.line_price for x in self.bmn_it_preventive_line ])+sum([x.line_price for x in self.bmn_it_remedial_line])
            bmn_vat += self.get_vat_total(self.bmn_it_preventive_line) + self.get_vat_total(self.bmn_it_remedial_line)
            profit = sale - cost 
            profit_per =0.0 
            if sale:
                profit_per = (profit/sale) * 100
        self.a_bmn_cost = cost 
        self.a_bmn_sale = sale 
        self.a_bmn_profit = profit 
        self.a_bmn_profit_percentage = profit_per
        self.a_bmn_vat = bmn_vat
        return {'cost':cost,'sale':sale,'vat':bmn_vat}
    def calculate_total_manpower_cost(self):
        cost= self.a_bim_cost + self.a_bmn_cost
        sale= self.a_bim_sale + self.a_bmn_sale
        vat = self.a_bim_vat + self.a_bmn_vat
        profit = sale -cost
        profit_per = 0.0 
        if sale:
            profit_per = (profit/sale) * 100
        self.a_total_manpower_cost = cost 
        self.a_total_manpower_sale = sale
        self.a_total_manpower_profit = profit
        self.a_total_manpower_profit_percentage = profit_per
        self.a_total_manpower_vat = vat
        return cost
        
        

    
    def calculate_om(self):
        sale =cost =profit=profit_per=vat =0.0
        if self.included_om_in_quotation:
            cost =sum([x.line_cost for x in self.om_residenteng_line ])
            sale =sum([x.line_price for x in self.om_residenteng_line ])
            vat += self.get_vat_total(self.om_residenteng_line)
            profit = sale - cost 
            profit_per =0.0 
            if sale:
                profit_per = (profit/sale) * 100
        self.a_om_cost = cost 
        self.a_om_sale = sale 
        self.a_om_profit = profit 
        self.a_om_profit_percentage = profit_per
        self.o_m_vat = vat
        return {'cost':cost,'sale':sale,'vat':vat}
    def calculate_bim_analy(self):
        result =[]
        result.append(self.calculate_imp())
        result.append(self.calculate_bmn())
        result.append(self.calculate_om())
        cost = sum([x['cost']for x in result])
        sale = sum([x['sale']for x in result])
        vat = sum([x['vat']for x in result])
        profit = sale - cost 
        profit_per =0.0
        if sale:
            profit_per = (profit/sale) * 100
        self.a_tot_cost = cost
        self.a_tot_sale = sale
        self.a_tot_profit = profit 
        self.a_tot_profit_percentage = profit_per
        self.a_tot_vat = vat
    
    def get_revenue_total(self,line_ids):
        sale = cost = 0.0
        for line in line_ids:
            sale += line.total_sale 
            cost += line.total_cost
        return sale,cost
            
    
    def summarize_revenue(self):
        sale =self.get_revenue_total(self.mat_group_weight_line)[0] + self.get_revenue_total(self.imp_weight_line)[0] + self.get_revenue_total(self.amc_weight_line)[0] + self.get_revenue_total(self.om_weight_line)[0]
        cost =self.get_revenue_total(self.mat_group_weight_line)[1] + self.get_revenue_total(self.imp_weight_line)[1] + self.get_revenue_total(self.amc_weight_line)[1] + self.get_revenue_total(self.om_weight_line)[1]
        profit = sale - cost
        profit_perc  =0.0 
        if sale:
            profit_perc = (profit /sale) *100 
        self.rev_tot_sale1 = sale 
        self.rev_tot_cost1 = cost 
        self.rev_profit1 = profit 
        self.rev_profit_percentage1 = profit_perc
    
    
    def get_weight_summary(self):
        res = {}
        for line in self.mat_group_weight_line:
            res[line.pdt_grp_id.id] = {'sale':line.total_sale,'sale_aftr_disc':line.sale_aftr_disc,'cost':line.total_cost,'manpower_cost':0.0}
        for line in self.extra_weight_line:
            data = res.get(line.pdt_grp_id.id,{})
            if data:
                data['sale'] += line.total_sale
                data['sale_aftr_disc'] += line.sale_aftr_disc 
                data['cost'] += line.total_cost
        for line in self.imp_weight_line:
            data = res.get(line.pdt_grp_id.id,{})
            if data:
                data['sale'] += line.total_sale
                data['sale_aftr_disc'] += line.sale_aftr_disc 
                data['cost'] += line.total_cost
                

        
        for line in self.amc_weight_line:
            data = res.get(line.pdt_grp_id.id,{})
            if data:
                data['sale'] += line.total_sale
                data['sale_aftr_disc'] += line.sale_aftr_disc 
                data['cost'] += line.total_cost
               
                
        
        for line in self.om_weight_line:
            data = res.get(line.pdt_grp_id.id,{})
            if data:
                data['sale'] += line.total_sale
                data['sale_aftr_disc'] += line.sale_aftr_disc 
                data['cost'] += line.total_cost

        print "res>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>,res",res
        return res
    
    
    
    def generate_summary_weight(self):
        result = self.get_weight_summary()
        data = []
        total_cost =0.0
        for key,val in result.iteritems():
            pdt_grp_id = key 
            sale = val.get('sale')
            sale_aftr_disc = val.get('sale_aftr_disc')
            cost = val.get('cost')
            total_cost += cost
            profit = sale_aftr_disc- cost
            data.append({'pdt_grp_id':pdt_grp_id,'total_sale':sale,'total_cost':cost,'sale_aftr_disc':sale_aftr_disc,'profit':profit,'total_gp':profit})
        
        
        if total_cost:
            total_manpower_cost = self.get_imp_cost() + self.get_bmn_cost()
            for val in data:
                cost = val.get('total_cost')
                manpower_cost = total_manpower_cost *(cost/total_cost)
                val['manpower_cost'] = manpower_cost
                profit = val.get('profit')
                total_gp = profit + manpower_cost 
                val['total_gp'] = total_gp
            
                
        
        self.summary_weight_line.unlink()
        self.summary_weight_line = data
    
    def pull_branch_div(self):
        if not self.od_branch_id:
            self.od_branch_id = self.lead_id and self.lead_id.od_branch_id and self.lead_id.od_branch_id.id or False
        if not self.od_division_id:
            self.od_division_id = self.lead_id and self.lead_id.od_division_id and self.lead_id.od_division_id.id or False
    
    def update_submit_date(self):
        if self.status == 'active' and self.submitted_date:
            self.lead_id.finished_on_7 =self.submitted_date[:10]
    
    @api.one
    def update_cost_sheet(self):
        self.recalculate()
        self.compute_value()
        self.compute_value_optional()
        self.summarize()
        self.log_calculate_cost()
        self.update_bim_summary()
        self.calculate_bim_analy()
        self.calculate_total_manpower_cost()
        self.update_opportunity()
        self.generate_group_weight()
        self.generate_brand_weight()
        self.generate_impl_weight()
        self.generate_amc_weight()
        self.generate_om_weight()
        self.generate_extra_weight()
        self.summarize_revenue()
        self.generate_summary_weight()
        self.pull_branch_div()
#         self.update_submit_date()
    
    def price_fix_line(self,line_id,xno=1):
        for line in line_id:
            unit_price = line.unit_price
            if xno ==2:
                unit_price = line.unit_price2
            line['new_unit_price'] = unit_price
            line['temp_unit_price'] = unit_price 
            line['fixed'] = True
    
    def price_unfix_line(self,line_id):
        for line in line_id:
            unit_price = line.new_unit_price
            line['temp_unit_price'] = unit_price 
            line['fixed'] = False
            
    
    @api.one
    def btn_price_fix(self):
        raise Warning("Working Progress.........")
        price_fixed = self.price_fixed 
        if price_fixed:
            self.price_unfix_line(self.mat_main_pro_line)
            self.price_unfix_line(self.mat_extra_expense_line)
            self.write({'price_fixed':False})
        else:
            self.price_fix_line(self.mat_main_pro_line)
            self.price_fix_line(self.mat_extra_expense_line,2)
            self.write({'price_fixed':True})
    
    
    
    def line_update_tax_id(self,line_ids):
        for line in line_ids:
            tax_id = line.group and line.group.tax_id and line.group.tax_id.id or False
            line.tax_id = tax_id
    
    def line_update_tax_id_1(self,line_ids):
        for line in line_ids:
            tax_id = line.group_id and line.group_id.tax_id and line.group_id.tax_id.id or False
            line.tax_id = tax_id
    
    def line_update_tax_id_2(self,line_ids):
        for line in line_ids:
            tax_id = line.group2 and line.group2.tax_id and line.group2.tax_id.id or False
            line.tax_id = tax_id
    
    def line_update_tax_id_costgroup(self,line_ids):
        for line in line_ids:
            tax_id = line.cost_group_id and line.cost_group_id.tax_id and line.cost_group_id.tax_id.id or False
            line.tax_id = tax_id

    def update_bim_tax_id(self):
        self.bim_tax_id = self.bim_log_group and self.bim_log_group.tax_id and self.bim_log_group.tax_id.id or False
    @api.one 
    def update_vat(self):
        self.line_update_tax_id(self.mat_main_pro_line)
        self.line_update_tax_id_1(self.mat_optional_item_line)
        self.line_update_tax_id_2(self.mat_extra_expense_line)
        
        self.line_update_tax_id(self.trn_customer_training_line)
        self.line_update_tax_id_2(self.trn_customer_training_extra_expense_line)
        
        self.line_update_tax_id(self.implimentation_extra_expense_line)
        self.line_update_tax_id_costgroup(self.manpower_manual_line)
        self.line_update_tax_id(self.bim_implementation_code_line)
        self.line_update_tax_id(self.oim_implimentation_price_line)
        self.line_update_tax_id(self.oim_extra_expenses_line)
        
        self.line_update_tax_id(self.bmn_it_preventive_line)
        self.line_update_tax_id(self.bmn_it_remedial_line)
        self.line_update_tax_id(self.bmn_spareparts_beta_it_maintenance_line)
        self.line_update_tax_id(self.bmn_beta_it_maintenance_extra_expense_line)
        self.line_update_tax_id(self.omn_out_preventive_maintenance_line)
        self.line_update_tax_id(self.omn_out_remedial_maintenance_line)
        self.line_update_tax_id(self.omn_spare_parts_line)
        self.line_update_tax_id(self.omn_maintenance_extra_expense_line)
        
        self.line_update_tax_id(self.om_residenteng_line)
        self.line_update_tax_id(self.om_eqpmentreq_line)
        self.line_update_tax_id(self.om_extra_line)
        
        self.update_bim_tax_id()
       
    
    
    
    
    @api.one
    def update_opportunity(self):
        if self.status == 'active' and self.state != 'draft':
            lead_id = self.lead_id and self.lead_id.id or False
            manpower_cost =self.calculate_total_manpower_cost()
            new_profit = self.sum_profit + manpower_cost
            sale = self.sum_total_sale
            profit_per =0.0
            if sale:
                profit_per = (new_profit/sale) * 100.0

            if lead_id:
                lead = self.lead_id
                vals ={
                      'planned_revenue':self.sum_total_sale,
                      'od_costsheet_manpower_cost':manpower_cost,
                      'od_costsheet_new_profit':new_profit,
                      'od_costsheet_new_profit_percent':profit_per,
                       }
                lead.write(vals)


    def get_min_max_manpower_percent(self,param):
        parameter_obj = self.env['ir.config_parameter']
        if self.is_saudi_comp():
            param = param + '_ksa'
        key =[('key', '=', param)]
        param_obj = parameter_obj.search(key)
        if not param_obj:
            raise Warning(_('Settings Warning!'),_('NoParameter Not defined\nconfig it in System Parameters with %s'%param))
        result = param_obj.value
        return result
    @api.one
    def log_calculate_cost(self):
        cost =0.0
        bim_extra_exp=self.material_extra_cost(self.implimentation_extra_expense_line)
        total_cost = self.mat_tot_cost + self.trn_tot_cost + self.oim_tot_cost + bim_extra_exp
        cost_factor = self.company_id.od_cost_factor
        if not cost_factor:
            raise Warning('Manpower Implementation Cost Factor Not Set in Your Company ,Please Configure It First')

        log_factor = self.company_id.od_log_factor
        if not log_factor:
            raise Warning('Manpower Implementation Log Factor Not Set in Your Company ,Please Configure It First')
        cost_fact = cost_factor/100
        cost_perc_value = 0.0
        if total_cost:
            cost_perc_value = (exp(log10(log_factor/(total_cost)))*cost_fact)
        cost_perc_min_val = float(self.get_min_max_manpower_percent('od_beta_it_min_manpower_percentage'))/100
        cost_perc_max_val = float(self.get_min_max_manpower_percent('od_beta_it_max_manpower_percentage'))/100
        print "cost perc value max min",cost_perc_value,cost_perc_max_val,cost_perc_min_val
        if cost_perc_value > cost_perc_max_val :
            print "its maximum exceeded"
            cost_perc_value =  cost_perc_max_val
        if cost_perc_value < cost_perc_min_val:
            print "its below minumum"
            cost_perc_value = cost_perc_min_val
        if total_cost:
            if self.bim_full_outsource:
                cost = (cost_perc_value * (total_cost)/2)
            else:
                print "cost_perc_value",cost_perc_value
                cost = (cost_perc_value * total_cost)
        self.bim_log_cost = cost
    @api.one
    def update_bim_summary(self):
        bim_total_cost = self.bim_tot_cost1
        bim_tot_sale = self.bim_tot_sale1
        imp_cost = self.line_single(self.bim_implementation_code_line)
        if self.bim_log_select:
            bim_total_cost += self.bim_log_cost
            bim_tot_sale += self.bim_log_price
        if self.bim_imp_select:
            bim_tot_sale += imp_cost.get('tot_sale')
            bim_total_cost += imp_cost.get('tot_cost')
        if self.included_bim_in_quotation:
            self.bim_tot_cost = bim_total_cost
            self.bim_tot_sale = bim_tot_sale
        else:
            self.bim_tot_cost = 0
            self.bim_tot_sale = 0
        self.bim_tot_cost1 = bim_total_cost
        self.bim_tot_sale1 = bim_tot_sale
        profit = bim_tot_sale - bim_total_cost
        profit_per = 0.0
        if bim_tot_sale:
            profit_per = (profit/bim_tot_sale) * 100
        if self.included_bim_in_quotation:
            self.bim_profit = profit
            self.bim_profit_percentage = profit_per
        else:
            self.bim_profit = 0
            self.bim_profit_percentage = 0
        self.bim_profit1 = profit
        self.bim_profit_percentage1 = profit_per
    @api.one
    def fill_renewal(self):
        self.fill_line()
        self.fill_line_optional()
        self.ren_filled = True

    @api.one
    def order_seq(self,lines):
        count = 0
        for line in lines:
            count += 1
            line.item = count
            line.item_int = count

    @api.one
    def mat_order(self):
        self.order_seq(self.mat_main_pro_line)
        self.order_seq(self.mat_optional_item_line)
        self.order_seq(self.mat_extra_expense_line)
    @api.one
    def trn_order(self):
        self.order_seq(self.trn_customer_training_line)
        self.order_seq(self.trn_customer_training_extra_expense_line)
    @api.one
    def reorder_seq(self):

        count = 0
        if self.env.context.get('optional'):
            line_id = self.ren_optional_item_line
        else:
            line_id = self.ren_main_pro_line
        for ren in line_id:
            count += 1
            ren.item = count
            ren.item_int = count
    @api.one
    def fill_line(self):
        vals = []
        for mat in self.mat_main_pro_line:
            if mat.ren:
                qty = int(mat.qty)
                for i in range(qty):
                    print i
                    vals.append([0,0,{
                                 'cost_sheet_id':self.id,
                                 'manufacture_id':mat.manufacture_id.id,
                                 'renewal_package_no':mat.part_no.id
                                 }])
        self.ren_main_pro_line =  vals

    @api.one
    def fill_line_optional(self):
        vals = []
        for mat in self.mat_optional_item_line:
            if mat.ren:
                qty = int(mat.qty)
                for i in range(qty):
                    print i
                    vals.append([0,0,{
                                 'cost_sheet_id':self.id,
                                 'manufacture_id':mat.manufacture_id.id,
                                 'renewal_package_no':mat.part_no.id
                                 }])
        self.ren_optional_item_line =  vals


    def line_two(self,line_id,lines):
        tot_sale =0.0
        tot_cost =0.0
        for line1 in lines:
            tot_cost += line1.line_cost
            tot_sale += line1.line_price
        for line in line_id:
            tot_sale += line.line_price
            tot_cost += line.line_cost_local_currency

        res={
             'tot_sale':tot_sale or 0.0,
             'tot_cost':tot_cost or 0.0,
             }
        return res


    
    def get_vat_total(self,line_id):
        return sum([line.vat_value for line in line_id])
    def get_vat_total2(self,line_id):
        return sum([line.vat_value2 for line in line_id])
    
    def line_summarize(self,line_id):
        tot_sale =0.0
        tot_cost =0.0
        for line in line_id:
            tot_sale += line.line_price
            tot_cost += line.line_cost_local_currency
        res = {
                'tot_sale':tot_sale or 0.0,
                'tot_cost':tot_cost or 0.0,
             }


        return res
    def line_summarize_optional(self,line_id):
        tot_sale =0.0
        tot_cost =0.0
        for line in line_id:
            tot_sale += line.line_price
            tot_cost += line.line_cost_local_currency
            print "line price,>>>>>>>>>total sale optioanal>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",line.line_price,tot_sale
        res={
             'tot_sale':tot_sale or 0.0,
             'tot_cost':tot_cost or 0.0,
             }


        return res

    def line_capture(self,first_line,second_line):
        tot_sale =0.0
        tot_cost =0.0
        for line in first_line:
            tot_cost += line.line_cost
        for line2 in second_line:
            tot_cost += line2.line_cost
            tot_sale += line2.line_price
        res = {
             'tot_sale':tot_sale or 0.0,
             'tot_cost':tot_cost or 0.0,
               }
        return res


    def line_single(self,lines):
        tot_sale =0.0
        tot_cost =0.0
        for line2 in lines:
            tot_cost += line2.line_cost
            tot_sale += line2.line_price
        res = {
             'tot_sale':tot_sale or 0.0,
             'tot_cost':tot_cost or 0.0,
               }
        return res

    def material_extra_cost(self,line_id):
        tot_cost =0.0
        for line in line_id:
            tot_cost += line.line_cost
        return tot_cost

    def material_extra_cost2(self,line_id):
        tot_cost =0.0
        for line in line_id:
            tot_cost += line.line_cost_local
        return tot_cost

    def material_extra_sale(self,line_id):
        tot_sale =0.0
        for line in line_id:
            tot_sale += line.line_price2
        return tot_sale


    @api.one
    def summarize(self):
        mat_res=self.line_summarize(self.mat_main_pro_line)
        mat_extra_cost = self.material_extra_cost2(self.mat_extra_expense_line) or 0.0
        mat_extra_sale = self.material_extra_sale(self.mat_extra_expense_line) or 0.0
        total_sale = mat_res.get('tot_sale') + mat_extra_sale
        total_cost = mat_res.get('tot_cost') + mat_extra_cost
        profit =  round(total_sale) - round(total_cost)
       
        profit_per =0.0
#         mat_vat = self.get_vat_total(self.mat_main_pro_line) + self.get_vat_total(self.mat_optional_item_line) + self.get_vat_total(self.mat_extra_expense_line)
        mat_main_vat = self.get_vat_total(self.mat_main_pro_line)  + self.get_vat_total2(self.mat_extra_expense_line)
        self.mat_vat1 = mat_main_vat
        if total_sale:
            profit_per = (profit/total_sale) * 100

        if self.included_in_quotation:
            self.mat_tot_sale = total_sale
            self.mat_tot_cost = total_cost
            self.mat_profit = profit
            self.mat_profit_percentage = profit_per
            self.mat_vat = mat_main_vat
        else:
            self.mat_tot_sale = 0
            self.mat_tot_cost = 0
            self.mat_profit = 0
            self.mat_vat =0.0
            self.mat_profit_percentage = 0

        #duplicate vals
        self.mat_tot_sale1 = total_sale
        self.mat_tot_cost1 = total_cost
        self.mat_profit1 = profit
        self.mat_profit_percentage1 = profit_per
        
        
        
        mat_optional = self.line_summarize_optional(self.mat_optional_item_line)
        opt_total_sale = mat_optional.get('tot_sale')
        opt_total_cost = mat_optional.get('tot_cost')
        opt_profit =  opt_total_sale - opt_total_cost
        opt_profit_per = 0.0
        opt_mat_vat = self.get_vat_total(self.mat_optional_item_line)
        if opt_total_sale:
            opt_profit_per = (opt_profit/opt_total_sale) * 100

        if self.included_in_quotation:
            self.mat_tot_sale_opt = opt_total_sale
            self.mat_tot_cost_opt = opt_total_cost
            self.mat_profit_opt = opt_profit
            self.mat_profit_percentage_opt = opt_profit_per
            self.mat_vat_opt = opt_mat_vat
        else:
            self.mat_tot_sale_opt = 0
            self.mat_tot_cost_opt = 0
            self.mat_profit_opt = 0
            self.mat_profit_percentage_opt = 0
            self.mat_vat_opt = 0.0

        trn_res = self.line_summarize(self.trn_customer_training_line)
        trn_extra =self.material_extra_cost2(self.trn_customer_training_extra_expense_line) or 0.0
        trn_extra_sale = self.material_extra_sale(self.trn_customer_training_extra_expense_line) or 0.0
        trn_total_sale = trn_res.get('tot_sale') + trn_extra_sale
        trn_total_cost = trn_res.get('tot_cost') + trn_extra
        trn_profit =  trn_total_sale - trn_total_cost
        trn_profit_per =0.0
        trn_vat = self.get_vat_total(self.trn_customer_training_line) + self.get_vat_total2(self.trn_customer_training_extra_expense_line) 

        if trn_total_sale:
            trn_profit_per = (trn_profit/trn_total_sale) * 100
        if self.included_trn_in_quotation:
            self.trn_tot_sale = trn_total_sale
            self.trn_tot_cost = trn_total_cost
            self.trn_profit = trn_profit
            self.trn_profit_percentage = trn_profit_per
            self.trn_vat = trn_vat
        else:
            self.trn_tot_sale = 0
            self.trn_tot_cost = 0
            self.trn_profit = 0
            self.trn_profit_percentage = 0
            self.trn_vat =0
        self.trn_tot_sale1 = trn_total_sale
        self.trn_tot_cost1 = trn_total_cost
        self.trn_profit1 = trn_profit
        self.trn_profit_percentage1 = trn_profit_per
        self.trn_vat1 =trn_vat         

        bim_res = self.line_single(self.manpower_manual_line)
        bim_extra = self.line_single(self.implimentation_extra_expense_line)
        bim_total_sale = bim_res.get('tot_sale',0.0) + bim_extra.get('tot_sale',0.0)
        bim_total_cost = bim_res.get('tot_cost',0.0) + bim_extra.get('tot_cost',0.0)
        bim_profit =  bim_total_sale - bim_total_cost
        bim_profit_per = 0.0
        bim_vat =  self.get_vat_total(self.implimentation_extra_expense_line) + self.get_vat_total(self.manpower_manual_line) + self.get_vat_total(self.bim_implementation_code_line) 
        if self.bim_log_select:
            bim_vat +=self.bim_log_vat_value
        if bim_total_sale:
            bim_profit_per = (bim_profit/bim_total_sale) * 100
        if self.included_bim_in_quotation:
            self.bim_tot_sale = bim_total_sale
            self.bim_tot_cost = bim_total_cost
            self.bim_profit = bim_profit
            self.bim_profit_percentage = bim_profit_per
            self.bim_vat = bim_vat
        else:
            self.bim_tot_sale = 0
            self.bim_tot_cost = 0
            self.bim_profit = 0
            self.bim_profit_percentage = 0
            self.bim_vat =0
        self.bim_tot_sale1 = bim_total_sale
        self.bim_tot_cost1 = bim_total_cost
        self.bim_profit1 = bim_profit
        self.bim_profit_percentage1 = bim_profit_per
        self.bim_vat1 = bim_vat
        
        oim_res = self.line_single(self.oim_implimentation_price_line)
        oim_extra = self.line_single(self.oim_extra_expenses_line)
        oim_total_sale = oim_res.get('tot_sale',0.0) + oim_extra.get('tot_sale',0.0)
        oim_total_cost = oim_res.get('tot_cost') + oim_extra.get('tot_cost',0.0)
        oim_profit =  oim_total_sale - oim_total_cost
        oim_profit_per = 0.0
        oim_vat = self.get_vat_total(self.oim_implimentation_price_line) +  self.get_vat_total(self.oim_extra_expenses_line) 
        
        if oim_total_sale:
            oim_profit_per = (oim_profit/oim_total_sale) * 100
        if self.included_bim_in_quotation:
            self.oim_tot_sale = oim_total_sale
            self.oim_tot_cost = oim_total_cost
            self.oim_profit = oim_profit
            self.oim_profit_percentage =  oim_profit_per
            self.oim_vat = oim_vat
        else:
            self.oim_tot_sale = 0
            self.oim_tot_cost = 0
            self.oim_profit = 0
            self.oim_profit_percentage =  0
            self.oim_vat =0

        self.oim_tot_sale1 = oim_total_sale
        self.oim_tot_cost1 = oim_total_cost
        self.oim_profit1 = oim_profit
        self.oim_profit_percentage1 =  oim_profit_per
        
        self.oim_vat1 = oim_vat
        

        bmn_res = self.line_single(self.bmn_it_preventive_line)
        bmn_rem = self.line_single(self.bmn_it_remedial_line)
        bmn_ext = self.line_two(self.bmn_spareparts_beta_it_maintenance_line, self.bmn_beta_it_maintenance_extra_expense_line)
        bmn_total_sale = bmn_res.get('tot_sale',0.0) + bmn_rem.get('tot_sale',0.0) + bmn_ext.get('tot_sale',0.0)
        bmn_total_cost = bmn_res.get('tot_cost') + bmn_rem.get('tot_cost',0.0) + bmn_ext.get('tot_cost',0.0)
        bmn_profit =  bmn_total_sale - bmn_total_cost
        bmn_profit_per = 0.0
        bmn_vat = self.get_vat_total(self.bmn_it_preventive_line) + self.get_vat_total(self.bmn_it_remedial_line) + self.get_vat_total(self.bmn_spareparts_beta_it_maintenance_line) + self.get_vat_total(self.bmn_beta_it_maintenance_extra_expense_line)

        if bmn_total_sale:
            bmn_profit_per = (bmn_profit/bmn_total_sale) * 100

        if self.included_bmn_in_quotation:
            self.bmn_tot_sale = bmn_total_sale
            self.bmn_tot_cost = bmn_total_cost
            self.bmn_profit = bmn_profit
            self.bmn_profit_percentage = bmn_profit_per
            self.bmn_vat = bmn_vat
        else:
            self.bmn_tot_sale = 0
            self.bmn_tot_cost = 0
            self.bmn_profit = 0
            self.bmn_profit_percentage = 0
            self.bmn_vat =0

        self.bmn_tot_sale1 = bmn_total_sale
        self.bmn_tot_cost1 = bmn_total_cost
        self.bmn_profit1 = bmn_profit
        self.bmn_profit_percentage1 = bmn_profit_per
        self.bmn_vat1 = bmn_vat
        omn_res = self.line_single(self.omn_out_preventive_maintenance_line)
        omn_res_rm = self.line_single(self.omn_out_remedial_maintenance_line)
        omn_extra = self.line_two(self.omn_spare_parts_line,self.omn_maintenance_extra_expense_line)
        omn_total_sale = omn_res.get('tot_sale',0.0) + omn_res_rm.get('tot_sale',0.0) + omn_extra.get('tot_sale',0.0)
        omn_total_cost = omn_res.get('tot_cost',0.0) + omn_res_rm.get('tot_cost',0.0) + omn_extra.get('tot_cost',0.0)
        omn_profit =  omn_total_sale - omn_total_cost
        omn_profit_per = 0.0
        omn_vat = self.get_vat_total(self.omn_out_preventive_maintenance_line) + self.get_vat_total(self.omn_out_remedial_maintenance_line) + self.get_vat_total(self.omn_spare_parts_line) + self.get_vat_total(self.omn_maintenance_extra_expense_line)

        if omn_total_sale:
            omn_profit_per = (omn_profit/omn_total_sale) * 100
        if self.included_bmn_in_quotation:
            self.omn_tot_sale = omn_total_sale
            self.omn_tot_cost = omn_total_cost
            self.omn_profit = omn_profit
            self.omn_profit_percentage = omn_profit_per
            self.omn_vat = omn_vat
        else:
            self.omn_tot_sale = 0
            self.omn_tot_cost = 0
            self.omn_profit = 0
            self.omn_profit_percentage = 0
            self.omn_vat = 0
            
        self.omn_tot_sale1 = omn_total_sale
        self.omn_tot_cost1 = omn_total_cost
        self.omn_profit1 = omn_profit
        self.omn_profit_percentage1 = omn_profit_per
        self.omn_vat1 = omn_vat
        om_res = self.line_two(self.om_eqpmentreq_line, self.om_extra_line)
        om_eng = self.line_single(self.om_residenteng_line)
        om_total_sale = om_res.get('tot_sale') + om_eng.get('tot_sale')
        om_total_cost = om_res.get('tot_cost') + om_eng.get('tot_cost')
        om_profit =  om_total_sale - om_total_cost
        om_profit_per = 0.0
        o_m_vat = self.get_vat_total(self.om_residenteng_line) + self.get_vat_total(self.om_eqpmentreq_line) +self.get_vat_total(self.om_extra_line)

        if om_total_sale:
            om_profit_per = (om_profit/om_total_sale) * 100
        if self.included_om_in_quotation:
            self.o_m_tot_sale = om_total_sale
            self.o_m_tot_cost = om_total_cost
            self.o_m_profit = om_profit
            self.o_m_profit_percentage = om_profit_per
            self.o_m_vat = o_m_vat
        else:
            self.o_m_tot_sale = 0
            self.o_m_tot_cost = 0
            self.o_m_profit = 0
            self.o_m_profit_percentage = 0
            self.o_m_vat = 0

        self.o_m_tot_sale1 = om_total_sale
        self.o_m_tot_cost1 = om_total_cost
        
        self.o_m_profit1 = om_profit
        self.o_m_profit_percentage1 = om_profit_per
        
        self.o_m_vat1 = o_m_vat

    @api.one
    @api.depends('mat_tot_cost','trn_tot_cost','mat_tot_cost','bim_tot_cost',
                 'oim_tot_cost','bmn_tot_cost','omn_tot_cost','o_m_tot_cost')
    def _get_sum_total_cost(self):
        self.summary_tot_cost = self.mat_tot_cost + self.trn_tot_cost + self.bim_tot_cost + \
        self.oim_tot_cost + self.bmn_tot_cost + self.omn_tot_cost + self.o_m_tot_cost

    @api.one
    @api.depends('summary_tot_cost','mat_tot_cost')
    def _get_weight(self):
        if self.summary_tot_cost:
            self.mat_weight = 100 * self.mat_tot_cost /(self.summary_tot_cost or 1.0)
            self.trn_weight = 100 * self.trn_tot_cost / (self.summary_tot_cost or 1.0)
            self.bim_weight = 100 * self.bim_tot_cost / (self.summary_tot_cost or 1.0)
            self.oim_weight = 100 * self.oim_tot_cost / (self.summary_tot_cost or 1.0)
            self.bmn_weight = 100 * self.bmn_tot_cost / (self.summary_tot_cost or 1.0)
            self.omn_weight = 100 * self.omn_tot_cost / (self.summary_tot_cost or 1.0)
            self.o_m_weight = 100 * self.o_m_tot_cost /(self.summary_tot_cost or 1.0)
#     Summary total
    @api.one
    @api.depends('mat_tot_sale','trn_tot_sale','bim_tot_sale',
                 'oim_tot_sale','bmn_tot_sale','omn_tot_sale','o_m_tot_sale'
                 )
    def _get_total_sum_price(self):
        self.mat_price = self.mat_tot_sale + self.trn_tot_sale
        self.imp_price = self.bim_tot_sale + self.oim_tot_sale
        self.maint_price = self.bmn_tot_sale + self.omn_tot_sale + self.o_m_tot_sale

    @api.one
    @api.depends('mat_tot_sale','mat_tot_cost','mat_weight',
                 'trn_tot_sale','trn_tot_cost','trn_weight',
                 'bim_tot_sale','bim_tot_cost','bim_weight',
                 'oim_tot_sale','oim_tot_cost','oim_weight',
                 'bmn_tot_sale','bmn_tot_cost','bmn_weight',
                 'omn_tot_sale','omn_tot_cost','omn_weight',
                 'o_m_tot_sale','o_m_tot_cost','o_m_weight',
                 'special_discount'
                 )
    def _get_total_summary(self):
        total_sale = self.mat_tot_sale + self.trn_tot_sale + self.bim_tot_sale + self.oim_tot_sale + self.bmn_tot_sale + self.omn_tot_sale + self.o_m_tot_sale
        sum_total_sale = total_sale + self.special_discount
        total_cost = self.mat_tot_cost + self.trn_tot_cost + self.bim_tot_cost + self.oim_tot_cost + self.bmn_tot_cost + self.omn_tot_cost + self.o_m_tot_cost
        profit = sum_total_sale - total_cost
        profit_per = 0.0
        if total_sale:
            profit_per = profit/sum_total_sale
        total_weight = self.mat_weight + self.trn_weight + self.bim_weight + self.oim_weight + self.bmn_weight + self.omn_weight + self.o_m_weight
        self.sum_tot_sale = total_sale
        self.sum_total_sale = sum_total_sale
        special_discount = self.special_discount 
        special_discount_vat = special_discount *.05
        self.special_discount_vat = special_discount_vat
        total_vat = self.mat_vat + self.trn_vat + self.bim_vat + self.oim_vat + self.bmn_vat + self.omn_vat + self.o_m_vat + special_discount_vat
        self.sum_vat = total_vat
        self.sum_total_with_vat = sum_total_sale + total_vat
        if special_discount and total_sale:
            disc_per = (special_discount/total_sale) *100
            self.sp_disc_percentage = disc_per
        self.sum_tot_cost = total_cost
        self.sum_profit = profit
        
#         total_manpower_cost = self.a_total_manpower_cost 
# #         new_profit = total_manpower_cost +profit
#         self.sum_od_new_profit = new_profit
        self.sum_profit_per = profit_per * 100
        self.sum_total_weight = total_weight


    def default_bmn_it_preventive_line(self):
        line = [{'item':"1",'description':'Beta IT Preventive Maintenance','qty':1}]
        return line
    def default_bmn_it_remedial_line(self):
        line = [{'item':"1",'name':'Beta IT Remedial Maintenance','qty':1}]
        return line
    def default_omn_preventive_line(self):
        line = [{'item':"1",'name':'Outsourced Preventive Maintenance','qty':1}]
        return line
    def default_omn_remedial_line(self):
        line = [{'item':"1",'name':'Outsourced Remedial Maintenance','qty':1}]
        return line


    def default_beta_service_line(self):
        currency = self.env.user.company_id.currency_id.id
        tax_id = self.env.user.company_id.od_tax_id  or False
        line = [
                {'name':' BIM','sales_currency_id':currency, 'tax_id':tax_id},
                {'name':'BMN','sales_currency_id':currency, 'tax_id':tax_id},
                {'name':'OIM','sales_currency_id':currency, 'tax_id':tax_id},
                {'name':'OMN','sales_currency_id':currency, 'tax_id':tax_id},
                {'name':'O&M','sales_currency_id':currency, 'tax_id':tax_id},
                ]
        return line





    def is_saudi_comp(self):
        res = False
        saudi_comp_id = self.get_saudi_company_id()
        user_comp_id = self.env.user.company_id.id
        if user_comp_id == saudi_comp_id:
            res = True
        return res

    def my_value(self,uae_val,saudi_val):
        res = uae_val
        if self.is_saudi_comp():
            res =saudi_val
        return res

    def get_shipping_value(self):
        res = self.my_value(5, 2)
        return res

    def get_custom(self):
        res = self.my_value(1, 5)
        return res

    def get_stock_provision(self):
        res = self.my_value(0.50,1)
        return res


    def default_costgroup_material_line(self):

        currency = self.env.user.company_id.currency_id
        currency2 = self.env.user.company_id and self.env.user.company_id.od_supplier_currency_id
        if not currency2:
            raise Warning("Please Configure Cost Group Default Supplier Currency In Company")
        # currency2 = self.env['res.currency'].search([('name','=','USM')]).id
        tax_id  = self.env.user.company_id.od_tax_id or False
        rate=self.env['res.currency']._get_conversion_rate(currency, currency2)
        exchange_fact = 1/rate
        exchange_fact= float_round(exchange_fact, precision_rounding=currency2.rounding)
        line = [{
                 'name':'Main',
                 'sales_currency_id':currency.id,
                 'round_up':4,
                 'supplier_currency_id':currency2.id,
                 'currency_exchange_factor':exchange_fact,
                 'shipping':self.get_shipping_value(),
                 'customs':self.get_custom(),
                 'stock_provision':self.get_stock_provision(),
                 'conting_provision':0.50,
                 'tax_id':tax_id
                 }]
        return line
    def default_costgroup_extra_expense_line(self):

        currency = self.env.user.company_id.currency_id
        currency2 = self.env.user.company_id and self.env.user.company_id.od_supplier_currency_id
        if not currency2:
            raise Warning("Please Configure Cost Group Default Supplier Currency In Company")
        # currency2 = self.env['res.currency'].search([('name','=','USM')]).id

        rate=self.env['res.currency']._get_conversion_rate(currency, currency2)
        exchange_fact = 1/rate
        exchange_fact= float_round(exchange_fact, precision_rounding=currency2.rounding)
        tax_id  = self.env.user.company_id.od_tax_id or False
        line = [{
                 'name':'Extra Expense',
                 'sales_currency_id':currency.id,
                 'round_up':4,
                 'customer_discount':100,
                 'supplier_currency_id':currency2.id,
                 'currency_exchange_factor':exchange_fact,
                 'shipping':self.get_shipping_value(),
                 'customs':self.get_custom(),
                 'stock_provision':self.get_stock_provision(),
                 'conting_provision':0.50,
                 'tax_id':tax_id
                 }]
        return line
    def default_costgroup_optional_line(self):
        currency = self.env.user.company_id.currency_id
        currency2 = self.env.user.company_id and self.env.user.company_id.od_supplier_currency_id
        if not currency2:
            raise Warning("Please Configure Cost Group Default Supplier Currency In Company")
        # from_currency,to_currency = self.env.user.company_id.currency_id,self.env['res.currency'].search([('name','=','USM')])
        rate= self.env['res.currency']._get_conversion_rate(currency, currency2)
        exchange_fact = 1/rate
        exchange_fact= float_round(exchange_fact, precision_rounding=currency2.rounding)
        tax_id  = self.env.user.company_id.od_tax_id or False
        line = [{
                 'name':'Optional',
                 'sales_currency_id':currency.id,
                  'round_up':4,
                 'supplier_currency_id':currency2.id,
                 'currency_exchange_factor':exchange_fact,
                 'shipping':self.get_shipping_value(),
                 'customs':self.get_custom(),
                 'stock_provision':self.get_stock_provision(),
                 'conting_provision':0.50,
                  'tax_id':tax_id
                 }]
        return line
    
    
    
    @api.one 
    @api.depends('sum_profit','a_bim_cost','a_bmn_cost')
    def _get_total_gp(self):
        self.total_gp = self.sum_profit + self.a_bim_cost + self.a_bmn_cost
    
    summary_tot_cost = fields.Float(string='Total Cost',compute='_get_sum_total_cost',store=True)
    sum_tot_sale = fields.Float(string="Total Sale",compute="_get_total_summary",store=True)
    sum_tot_cost = fields.Float(string='Total Cost',compute="_get_total_summary",store=True)
    sum_profit = fields.Float(string="Total Profit",compute="_get_total_summary",store=True)
    total_gp = fields.Float(string="Total GP",compute="_get_total_gp")
#     sum_od_new_profit = fields.Float(string="New Profit",compute="_get_total_summary",store=True)
    sum_profit_per = fields.Float(string="Total Profit Percentage",compute="_get_total_summary",store=True)
    sum_total_weight = fields.Float(string="Total Weight",compute="_get_total_summary",store=True)
    special_discount = fields.Float(string="Special Discount") 
    special_discount_vat = fields.Float(string="Discount VAT",compute="_get_total_summary",store=True)
    sum_total_sale =fields.Float(string="Total Sale Final",compute="_get_total_summary",store=True)
    sum_total_with_vat =  fields.Float(string="Total Sale With VAT",compute="_get_total_summary",store=True)
    sum_vat = fields.Float(string="Total VAT",compute="_get_total_summary",store=True)
    sp_disc_percentage = fields.Float(string="Special Discount",digits=(12,6),compute="_get_total_summary",store=True)
    @api.onchange('bim_log_select')
    def onchange_bim_log_select(self):
        if self.bim_log_select:
            self.bim_imp_select = False

    @api.onchange('bim_imp_select')
    def onchange_bim_imp_select(self):
        if self.bim_imp_select:
            self.bim_log_select = False
    def default_section_material(self):
        line = [{'section':'M','name':'Main Material'}]
        return line
    def default_section_optional(self):
        line = [{'section':'O','name':'Optional Material'}]
        return line
    def default_section_training(self):
        line = [{'section':'T','name':'Training'}]
        return line
    def default_resident_eng_line(self):
        line = [{'name':'Resident Engineer'}]
        return line
    def default_exclusion_note(self):
        res = """
        <h4>* Work on any equipment not covered by this proposal</h4>
<h4>* Obtaining any required 3rd Party NOCs (No Objection Certificates: Municipality, Telecom, etc.), if any is required</h4>
<h4>* Electrical, Mechanical, and Civil Works</h4>
        """

        return res
    def default_amc_scope(self):
        res = """
        <h2><strong><span style="text-decoration: underline; color: blue;">Scope of Maintenance</span></strong></h2>
<table width="576">
<tbody>
<tr>
<td colspan="4" width="256">Note: This section represents maintenance services. They are different from the manufacturer services (such as warranty, subscriptions, and licenses renewals)</td>
<td width="64">&nbsp;</td>
<td style="text-align: right;" colspan="4" width="256">ملاحظة: يمثل هذا القسم الخدمات الفنية في الصيانة. هذه الخدمات تختلف عن خدمات الشركة المصنعة التي تتمثل في الضمان، الاشتراكات، وتجديد الرخص.</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td colspan="2" width="128"><strong>Start Date of Maintenance</strong></td>
<td style="text-align: center;" colspan="5" width="320">After Project Completion and Satisfaction of its Payments<br /> بعد انتهاء أعمال المشروع واتمام دفعاته</td>
<td style="text-align: right;" colspan="2" width="128"><strong>تاريخ بداية أعمال الصيانة</strong></td>
</tr>
<tr>
<td colspan="2"><strong>Duration of Maint.</strong></td>
<td style="text-align: center;" colspan="5">One Year - سنة واحدة</td>
<td style="text-align: right;" colspan="2"><strong>مدة أعمال الصيانة</strong></td>
</tr>
<tr>
<td colspan="2" rowspan="2"><strong>Maintenance Level</strong></td>
<td style="text-align: center;" colspan="5">8x5</td>
<td style="text-align: right;" colspan="2" rowspan="2"><strong>مستوى الصيانة</strong></td>
</tr>
<tr>
<td style="text-align: center;" colspan="5">Excluding Public Holidays <br /> غير شاملة للعطل الرسمية</td>
</tr>
<tr>
<td colspan="2"><strong>Preventive Maint.</strong></td>
<td style="text-align: center;" colspan="5">Quarterly - كل ربع سنة</td>
<td style="text-align: right;" colspan="2"><strong>الصيانة الوقائية الدورية</strong></td>
</tr>
<tr>
<td colspan="2" width="128"><strong>No. of Preventive </strong><br /><strong> Maintenances / Year</strong></td>
<td style="text-align: center;" colspan="5" width="320">4 Each Year</td>
<td style="text-align: right;" colspan="2" width="128"><strong>عدد مرات الصيانة الوقائية الدورية في السنة</strong></td>
</tr>
<tr>
<td colspan="2" width="128"><strong>Scope of Services </strong></td>
<td style="text-align: left;" colspan="5" width="320">&nbsp;Maintenance</td>
<td style="text-align: right;" colspan="2" width="128"><strong>نطاق الخدمات</strong></td>
</tr>
<tr>
<td colspan="2" rowspan="4" width="128"><strong>Remedial Maintenances</strong><br /> <br /><strong> Devices covered by this service must be covered by manufacturer warranty</strong></td>
<td style="text-align: center;" colspan="5" width="320"><strong>Level 1 Support</strong> - Customer Responsibility: <br /> (مسؤولية العميل)<br /> Problem Reporting and Basic Information<br /> الابلاغ عن الأعطال وجمع المعلومات الأولية</td>
<td style="text-align: right;" colspan="2" rowspan="4" width="128"><strong>الصيانة العلاجية</strong><br /> <br /><strong> يجب أن تكون الأجهزة المشمولة بهذه الخدمات خاضعة للضمان لدى الشركة المصنعة</strong></td>
</tr>
<tr>
<td style="text-align: center;" colspan="5" width="320"><strong>Level 2 Support</strong> - Beta IT Responsibility:<br /> (مسؤولية بيتا) <br /> Troubleshooting and Workaround<br /> العمل على حل الأعطال</td>
</tr>
<tr>
<td style="text-align: center;" colspan="5" width="320"><strong>Level 3 Support</strong> - Beta IT / Manufacturer Responsibility:<br /> (مسؤولية بيتا والشركة المصنعة)<br /> Root Cause Analysis (Provided that Customer has valid warranty and support with manufacturer)<br /> إيجاد جذور المشكلة للعطل ومنع تكرارها <br /> (يتطلب ذلك من العميل أن يبقي الأجهزة خاضعة لضمان الشركة المصنعة)</td>
</tr>
<tr>
<td style="text-align: center;" colspan="5" width="320"><strong>Level 4 Support</strong> - Manufacturer Responsibility:<br /> (مسؤولية الشركة المصنعة) <br /> Root access, Engineering, and Development (Requires customer to have valid warranty and support from manufacturer)<br /> هندسة البرامج والوصول إلى جوهر البرمجيات العاملة على الأجهزة وتطويرها لحل الأعطال المستعصية <br /> &nbsp;(يتطلب ذلك من العميل أن يبقي الأجهزة خاضعة لضمان الشركة المصنعة)</td>
</tr>
<tr>
<td colspan="2" rowspan="2" width="128"><strong>Warranty</strong><br /> <br /><strong> Devices covered by this service must be covered by manufacturer warranty</strong></td>
<td colspan="5" width="320">Beta IT will process RMA process on behalf of customer for malfunctioning devices provided that customer has a valid support contract with manufacturer and as per manufacturer terms and conditions.<br /> <br /> Material, covered by manufacturer warranty services, is subject to manufacturer warranty and RMA policies, procedures, and RMA repair periods. RMA and Manufactures' support conditions are provided by each manufacturer on its own web site.</td>
<td style="text-align: right;" colspan="2" rowspan="2" width="128"><strong>الضمان</strong><br /> <br /><strong> يجب أن تكون الأجهزة المشمولة بهذه الخدمات خاضعة للضمان لدى الشركة المصنعة</strong></td>
</tr>
<tr>
<td style="text-align: right;" colspan="5" width="320">ستقوم بيتا بالعمل على شحن الأجهزة المتعطلة للشركة المصنعة باسم العميل بشرط توفر عقد الضمان بين العميل والشركة المصنعة وحسب شروط الشركة المصنعة.<br /> <br /> تخضع المواد، المغطاة بخدمات الضمان من الشركات المصنعة، لشروط هذه الشركات فيما يتعلق لشروط الإصلاح وآلياته والزمن المطلوب لذلك. يمكن للعميل مراجعة هذه الشروط والآليات على المواقع الإلكترونية للشركات المصنعة للمواد المعروضة.</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td colspan="4">
<h3><span style="text-decoration: underline;"><strong>Fault Classification / Response Times</strong></span></h3>
</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4">
<h3><span style="text-decoration: underline;"><strong>جدول تصنيف أحداث الصيانة / أوقات الاستجابة</strong></span></h3>
</td>
</tr>
<tr>
<td colspan="3"><strong>A. Critical - Service Affecting</strong></td>
<td colspan="3" width="192">Any highly critical system or service outage in a live environment that results in severe degradation of overall on-line/off-line network performance.</td>
<td style="text-align: right;" colspan="3"><strong>أ. حرجة - تؤثر على سير العمل</strong></td>
</tr>
<tr>
<td colspan="3">Response Mean: Phone &amp; Email</td>
<td style="text-align: center;" colspan="3" width="192">One Business Hour<br /> خلال ساعة عمل واحدة</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: التلفون والبريد الاكتروني</td>
</tr>
<tr>
<td colspan="3">Response Mean: Remote Access</td>
<td style="text-align: center;" colspan="3" width="192">2 Business Hours<br /> خلال 2 ساعة عمل</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: الاتصال بالأنظمة عن بعد</td>
</tr>
<tr>
<td colspan="3">Response Mean: On-Site</td>
<td style="text-align: center;" colspan="3" width="192">4 Business Hours + Travelling Time<br /> &nbsp;خلال 4 ساعات عمل + وقت السفر والانتقال</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: الوصول إلى موقع العمل</td>
</tr>
<tr>
<td colspan="3"><strong>B. Major - Service Affecting</strong></td>
<td colspan="3" width="192">Any major degradation of system or service performance that impacts end user service quality or significantly impairs network operator control or operational effectiveness.</td>
<td style="text-align: right;" colspan="3"><strong>ب. كبيرة - تؤثر على سير العمل</strong></td>
</tr>
<tr>
<td colspan="3">Response Mean: Phone &amp; Email</td>
<td style="text-align: center;" colspan="3" width="192">One Business Hour<br /> خلال ساعة عمل واحدة</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: التلفون والبريد الاكتروني</td>
</tr>
<tr>
<td colspan="3">Response Mean: Remote Access</td>
<td style="text-align: center;" colspan="3" width="192">4 Business Hours<br /> خلال 4 ساعات عمل</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: الاتصال بالأنظمة عن بعد</td>
</tr>
<tr>
<td colspan="3">Response Mean: On-Site</td>
<td style="text-align: center;" colspan="3" width="192">7 Business Hours + Travelling Time<br /> &nbsp;خلال 7 ساعات عمل + وقت السفر والانتقال</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: الوصول إلى موقع العمل</td>
</tr>
<tr>
<td colspan="3"><strong>C. Minor - Not-Service Affecting</strong></td>
<td colspan="3" width="192">Any minor degradation of system or service performance that does not have any impact on end user service quality and minimal impact on network operations.</td>
<td style="text-align: right;" colspan="3"><strong>ج. صغيرة - لا تؤثر على سير العمل</strong></td>
</tr>
<tr>
<td colspan="3">Response Mean: Phone &amp; Email</td>
<td style="text-align: center;" colspan="3" width="192">24 Business Hour<br /> خلال 24 ساعة عمل</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: التلفون والبريد الاكتروني</td>
</tr>
<tr>
<td colspan="3">Response Mean: Remote Access</td>
<td style="text-align: center;" colspan="3" width="192">48 Business Hours<br /> خلال 48 ساعة عمل</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: الاتصال بالأنظمة عن بعد</td>
</tr>
<tr>
<td colspan="3">Response Mean: On-Site</td>
<td style="text-align: center;" colspan="3" width="192">72 Business Hours + Travelling Time<br /> &nbsp;خلال 72 ساعة عمل + وقت السفر والانتقال</td>
<td style="text-align: right;" colspan="3">آلية الاستجابة: الوصول إلى موقع العمل</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td colspan="4">
<h3><strong><span style="text-decoration: underline;">Escalation Sequence / Matrix</span></strong></h3>
</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4">
<h3><span style="text-decoration: underline;"><strong>إجراء العمل للإبلاغ عن أعمال الصيانة</strong></span></h3>
</td>
</tr>
<tr>
<td colspan="2" rowspan="4" width="128">Beta IT Helpdesk Contact Information</td>
<td rowspan="2" width="64">United Arab Emirates</td>
<td style="text-align: center;" colspan="3">&nbsp;+971 4 250 0111</td>
<td style="text-align: right;" rowspan="2" width="64">الإمارات العربية المتحدة</td>
<td style="text-align: right;" colspan="2" rowspan="4" width="128">معلومات الاتصال بقسم الصيانة - مكتب خدمات ما بعد البيع</td>
</tr>
<tr>
<td style="text-align: center;" colspan="3"><a href="mailto:support@betait.net">support@betait.net</a></td>
</tr>
<tr>
<td rowspan="2" width="64">Saudi Arabia</td>
<td style="text-align: center;" colspan="3">920006069</td>
<td style="text-align: right;" rowspan="2" width="64">المملكة العربية السعودية</td>
</tr>
<tr>
<td style="text-align: center;" colspan="3"><a href="mailto:support@sa.betait.net">support@sa.betait.net</a></td>
</tr>

<tr>
<td style="text-align: center;" colspan="3"><a href="mailto:khalid.lebbeh@betait.net">khalid.lebbeh@betait.net</a></td>
</tr>
<tr>
<td rowspan="2" width="64">Saudi Arabia</td>
<td style="text-align: center;" colspan="3">&nbsp; +966 50 343 2038</td>
<td style="text-align: right;" rowspan="2" width="64">المملكة العربية السعودية</td>
</tr>
<tr>
<td style="text-align: center;" colspan="3"><a href="mailto:wael.khalaf@sa.betait.net">fakhri.amaireh@sa.betait.net</a></td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td colspan="4" width="256">Any new configuration and configuration changes or additions to configuration will not be covered by this proposal. Moving systems is not covered by this proposal.</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4" width="256">لا تشمل هذه الخدمات أية تعريفات إضافية أو تغييرات في التعريفات على الأجهزة. كذلك لا تشمل هذه الخدمات نقل الأجهزة من مكان إلى آخر.</td>
</tr>
<tr>
<td colspan="4" width="256">Customer DOES NOT have access to Beta IT stock spare parts for workaround solutions during RMA periods.</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4" width="256">ليس للعميل الحق في استخدام أجهزة أخرى في مستودعات بيتا خلال فترة شحن الأجهزة المتعطلة تحت خدمة الضمان كبديل مؤقت إلى حين اتمام إعادة الأجهزة المتعطلة.</td>
</tr>
<tr>
<td colspan="4" width="256">If the customer requests a job that is not related to the AMC material or services mentioned in this document, then Beta IT reserves the right to not respond to this request and this shall not affect the progress or the due payments.</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4" width="256">إذا طلب العميل خدمة صيانة على أجهزة غير مشمولة في هذا العرض، فإنه يحق لشركة بيتا أن لا تستجيب لهذا الطلب ولا ينبغي أن يؤثر ذلك على مستحقات شركة بيتا.</td>
</tr>
<tr>
<td colspan="4" width="256">Beta IT reserves the right to assign, terminate, and re-assign subcontractors in a manner that allows Beta IT to perform the Services as described in the statement of work and in accordance with the terms of this agreement.</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4" width="256">يحق لشركة بيتا أن تستعين بمقاولين بالباطن لتقديم الخدمات المطلوبة المشروحة في نطاق الخدمة أعلاه وحسب شروط هذه الخدمات.</td>
</tr>
<tr>
<td colspan="4" width="256">Customer shall use and operate the Hardware and/or Software component(s) under this service agreement in accordance with manufacturer&rsquo;s operating manuals and promptly and regularly carry out all operation maintenance routine as and when specified.</td>
<td>&nbsp;</td>
<td style="text-align: right;" colspan="4" width="256">ينبغي أن يقوم العميل بتشغيل الأجهزة والبرمجيات الخاضعة لهذه الخدمات حسب شروط الشركات المصنعة للتشغيل كالتبريد، والكهرباء وغيرها. كما ينبغي أن يجري عليها الصيانة المطلوبة لضمان تشغيلها.</td>
</tr>
</tbody>
</table>
        """
        return res
    # def payment_d efaults(self):
    #     line = [{
    #              'payment_name':'Advanced Payment With Order',
    #              'payment_percentage':'40 %'
    #              },
    #             {
    #              'payment_name':'Upon Material Delivery',
    #              'payment_percentage':'40 %'
    #              },
    #               {
    #              'payment_name':'Upon Project Completion',
    #              'payment_percentage':'20 %'
    #              },
    #             {
    #              'payment_name':'Maintenance Contract / AMC',
    #              'payment_percentage':'60% Upon Start of Maintenance, Remaining to be paid on equal values periodically at the beginning of each quarter'
    #              },
    #              {
    #              'payment_name':'Warranty / Subscriptions / Licenses',
    #              'payment_percentage':'In case Warranty Contract / Subscription Licenses are supplied independently then, 100% of its value to be paid advanced'
    #              },
    #             ]
    #     return line

    state = fields.Selection([('draft','Draft'),('design_ready','Design Ready'),('submitted','Submit To Customer'),('returned_by_pmo','Returned By PMO'),
                              ('handover','Hand-Over'),('waiting_po','Waiting PO'),('returned_by_fin','Returned By Finance'),('change','Change'),('analytic_change','Redistribute Analytic'),('processed','Processed'),
                              ('modify','Modify'),('approved','Approved'),('done','Done'),('cancel','Cancelled')],string="Status",default='draft',track_visibility='always')
    ren_filled = fields.Boolean('Ren Filled')
    od_attachement_count = fields.Integer(string="Attachement Count",compute="_od_attachement_count"
                                          )

    #detailed summary Material
    mat_tot_sale = fields.Float('Material Total Sales',readonly=True,track_visibility='always')
    mat_tot_cost = fields.Float('Material Total Cost',readonly=True)
    mat_profit = fields.Float('Material Profit',readonly=True)
    mat_profit_percentage = fields.Float('Material Profit %',readonly=True)
    mat_weight = fields.Float('Material Weight %',compute='_get_weight',store=True)
    mat_vat = fields.Float(string="Material VAT",readonly=True)
    
    
    mat_tot_sale1 = fields.Float('Material Total Sales',readonly=True)
    mat_tot_cost1 = fields.Float('Material Total Cost',readonly=True)
    mat_profit1 = fields.Float('Material Profit',readonly=True)
    mat_vat1 = fields.Float(string="Material VAT",readonly=True)
    mat_profit_percentage1 = fields.Float('Material Profit %',readonly=True)

#detailed summary Material optional
    mat_tot_sale_opt = fields.Float('Material Total Sales',readonly=True)
    mat_tot_cost_opt = fields.Float('Material Total Cost',readonly=True)
    mat_profit_opt = fields.Float('Material Profit',readonly=True)
    mat_profit_percentage_opt = fields.Float('Material Profit %',readonly=True)
    mat_weight_opt = fields.Float('Material Weight %')
    mat_vat_opt = fields.Float(string="Material VAT OPT",readonly=True)

    trn_tot_sale = fields.Float('Training Total Sales',readonly=True)
    trn_tot_cost = fields.Float('Training Total Cost',readonly=True)
    trn_profit = fields.Float('Training Profit',readonly=True)
    trn_profit_percentage = fields.Float('Training Profit %',readonly=True)
    trn_weight = fields.Float('Training Weight %',compute='_get_weight',store=True)
    trn_vat = fields.Float(string="Training Vat",readonly=True)

    trn_tot_sale1 = fields.Float('Training Total Sales',readonly=True)
    trn_tot_cost1 = fields.Float('Training Total Cost',readonly=True)
    trn_profit1 = fields.Float('Training Profit',readonly=True)
    trn_profit_percentage1 = fields.Float('Training Profit %',readonly=True)
    trn_vat1 = fields.Float(string="Training Vat",readonly=True)
    #detailed summary Beta It Manpower Calculation

    bim_tot_sale = fields.Float('Bim Total Sales',readonly=True)
    bim_tot_cost = fields.Float('Bim Total Cost',readonly=True)
    bim_profit = fields.Float('Bim Profit',readonly=True)
    bim_profit_percentage = fields.Float('Bim Profit %',readonly=True)
    bim_weight = fields.Float('Bim Weight %',compute='_get_weight',store=True)
    bim_vat = fields.Float(string="Bim Vat",readonly=True)

    bim_tot_sale1 = fields.Float('Bim Total Sales',readonly=True)
    bim_tot_cost1 = fields.Float('Bim Total Cost',readonly=True)
    bim_profit1 = fields.Float('Bim Profit',readonly=True)
    bim_profit_percentage1 = fields.Float('Bim Profit %',readonly=True)
    bim_vat1 = fields.Float(string="Bim Vat",readonly=True)
    #detailed summary Outsourced Implementation Service

    oim_tot_sale = fields.Float('Oim Total Sales',readonly=True)
    oim_tot_cost = fields.Float('Oim Total Cost',readonly=True)
    oim_profit = fields.Float('Oim Profit',readonly=True)
    oim_profit_percentage = fields.Float('Oim Profit %',readonly=True)
    oim_weight = fields.Float('Oim Weight %',compute='_get_weight',store=True)
    oim_vat = fields.Float(string="Oim Vat",readonly=True)

    oim_tot_sale1 = fields.Float('Oim Total Sales',readonly=True)
    oim_tot_cost1 = fields.Float('Oim Total Cost',readonly=True)
    oim_profit1 = fields.Float('Oim Profit',readonly=True)
    oim_profit_percentage1 = fields.Float('Oim Profit %',readonly=True)
    oim_vat1 = fields.Float(string="Oim Vat",readonly=True)
    #detailed summary Beta IT Maintenance Services

    bmn_tot_sale = fields.Float('Bmn Total Sales',readonly=True)
    bmn_tot_cost = fields.Float('Bmn Total Cost',readonly=True)
    bmn_profit = fields.Float('Bmn Profit',readonly=True)
    bmn_profit_percentage = fields.Float('Bmn Profit %',readonly=True)
    bmn_weight = fields.Float('Bmn Weight %',compute='_get_weight',store=True)
    bmn_vat = fields.Float(string="Bmn Vat",readonly=True)

    bmn_tot_sale1 = fields.Float('Bmn Total Sales',readonly=True)
    bmn_tot_cost1 = fields.Float('Bmn Total Cost',readonly=True)
    bmn_profit1 = fields.Float('Bmn Profit',readonly=True)
    bmn_profit_percentage1 = fields.Float('Bmn Profit %',readonly=True)
    bmn_vat1 = fields.Float(string="Bmn Vat",readonly=True)
    #detailed summary Out Sourced Maintenance Service

    omn_tot_sale = fields.Float('Omn Total Sales',readonly=True)
    omn_tot_cost = fields.Float('Omn Total Cost',readonly=True)
    omn_profit = fields.Float('Omn Profit',readonly=True)
    omn_profit_percentage = fields.Float('Omn Profit %',readonly=True)
    omn_weight = fields.Float('Omn Weight %',compute='_get_weight',store=True)
    omn_vat = fields.Float(string="Omn Vat",readonly=True)

    omn_tot_sale1 = fields.Float('Omn Total Sales',readonly=True)
    omn_tot_cost1 = fields.Float('Omn Total Cost',readonly=True)
    omn_profit1 = fields.Float('Omn Profit',readonly=True)
    omn_profit_percentage1 = fields.Float('Omn Profit %',readonly=True)
    omn_vat1 = fields.Float(string="Omn Vat",readonly=True)
    
    #detailed summary Operation And Maintenance Service

    o_m_tot_sale = fields.Float('Op Total Sales',readonly=True)
    o_m_tot_cost = fields.Float('Op Total Cost',readonly=True)
    o_m_profit = fields.Float('Op Profit',readonly=True)
    o_m_profit_percentage = fields.Float('Op Profit %',readonly=True)
    o_m_weight = fields.Float('Op Weight %',compute='_get_weight',store=True)
    o_m_vat = fields.Float(string="Op Vat",readonly=True)

    o_m_tot_sale1 = fields.Float('Op Total Sales',readonly=True)
    o_m_tot_cost1 = fields.Float('Op Total Cost',readonly=True)
    o_m_profit1 = fields.Float('Op Profit',readonly=True)
    o_m_profit_percentage1 = fields.Float('Op Profit %',readonly=True)
    o_m_vat1 = fields.Float(string="Op Vat",readonly=True)
    
    #revenu
    rev_tot_sale1 = fields.Float('Rev Total Sales',readonly=True)
    rev_tot_cost1 = fields.Float('Rev Total Cost',readonly=True)
    rev_profit1 = fields.Float('Rev Profit',readonly=True)
    rev_profit_percentage1 = fields.Float('Rev Profit %',readonly=True)
    rev_vat1 = fields.Float(string="Op Vat",readonly=True)
    
    #Material11
    des_mat_e = fields.Char(string='Description')
    des_mat_a = fields.Char(string='Description')
    mat_price = fields.Float(string='Total Price',compute='_get_total_sum_price',store=True)
    #implementation
    des_imp_e = fields.Char(string='Description')
    des_imp_a = fields.Char(string='Description')
    imp_price = fields.Float(string='Total Price',compute='_get_total_sum_price',store=True)
    #maintanance
    des_maint_e = fields.Char(string='Description')
    des_maint_a = fields.Char(string='Description')
    maint_price = fields.Float(string='Total Price',compute='_get_total_sum_price',store=True)
    #operation and maintance
    des_op_e = fields.Char(string='Description')
    des_op_a = fields.Char(string='Description')
    op_price = fields.Float(string='Total Price')
    


    #Bim Log function Cost Fields
    bim_log_price = fields.Float('Price',compute='compute_bim_log_price')
    bim_log_cost = fields.Float('Cost',readonly=True)
    bim_log_group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group',copy=True)
    bim_tax_id  = fields.Many2one('account.tax',string="Tax")
    bim_log_vat = fields.Float(string="VAT %",compute="_compute_bim_vat")
    bim_log_vat_value = fields.Float(string="VAT Value",compute="_compute_bim_vat",)

    bim_log_select = fields.Boolean('Select')
    bim_imp_select = fields.Boolean('Select')
    bim_full_outsource = fields.Boolean('Full Outsource')
    
    
    
#     @api.onchange('bim_tax_id','bim_log_price')
#     def onchange_vat(self):
#         bim_tax_id = self.bim_tax_id
#         if bim_tax_id:
#             self.bim_log_vat = bim_tax_id.amount
#             self.bim_log_vat_value = self.bim_log_price * bim_tax_id.amount
    @api.one
    @api.depends('bim_tax_id','bim_log_price')
    def _compute_bim_vat(self):
        bim_tax_id = self.bim_tax_id
        if bim_tax_id:
            self.bim_log_vat = bim_tax_id.amount *100
            self.bim_log_vat_value = self.bim_log_price * bim_tax_id.amount
            
    
    #analysis purpose for mamoun
    a_bim_sale = fields.Float('Bim  Sales',readonly=True)
    a_bim_cost = fields.Float('Bim Cost',readonly=True)
    a_bim_profit = fields.Float('Bim Profit',readonly=True)
    a_bim_profit_percentage = fields.Float('Bim Profit %',readonly=True)
    a_bim_vat = fields.Float(string="Bim Vat",readonly=True)
    #Bmn
    a_bmn_sale = fields.Float('Bmn  Sales',readonly=True)
    a_bmn_cost = fields.Float('Bmn Cost',readonly=True)
    a_bmn_profit = fields.Float('Bmn Profit',readonly=True)
    a_bmn_profit_percentage = fields.Float('Bmn Profit %',readonly=True)
    a_bmn_vat = fields.Float(string="Bmn Vat",readonly=True)
    
    #
   
    a_total_manpower_sale = fields.Float('Manpower Sales',readonly=True)
    a_total_manpower_cost = fields.Float('Manpower Cost',readonly=True)
    a_total_manpower_profit = fields.Float('Manpower Profit',readonly=True)
    a_total_manpower_profit_percentage= fields.Float('Manpower Profit %',readonly=True)
    a_total_manpower_vat = fields.Float(string="Manpower Vat",readonly=True)
    #O&M
    a_om_sale = fields.Float('Om  Sales',readonly=True)
    a_om_cost = fields.Float('Om Cost',readonly=True)
    a_om_profit = fields.Float('Om Profit',readonly=True)
    a_om_profit_percentage = fields.Float('Om Profit %',readonly=True)
    a_om_vat = fields.Float(string="OM Vat",readonly=True)
    
    #total
    a_tot_sale = fields.Float('Total Sales',readonly=True)
    a_tot_cost = fields.Float('Total Cost',readonly=True)
    a_tot_profit = fields.Float('Total Profit',readonly=True)
    a_tot_profit_percentage = fields.Float('Total Profit %',readonly=True)
    a_tot_vat = fields.Float(string="Total Vat",readonly=True)
    #end
    
    status = fields.Selection([('active','Active'),('revision','Revision'),('cancel','Cancel'),('baseline','Baseline')],'Status',required=True,default='active')
    proposal_validity_duration = fields.Text(string="Proposal Validity Starting from its Date")
    show_proposal_validity = fields.Boolean(string="Show To Customer",default=True)
    baseline_sheet_ref = fields.Char("Baseline Cost Sheet Reference",readonly=True)
    date = fields.Date(string="Submission Date",default=fields.Date.today)
    lead_id = fields.Many2one('crm.lead',string='Opportunity',readonly="1",copy=True,required=True)
    lead_created_by = fields.Many2one('res.users',string="Lead Created By",related="lead_id.create_uid",store=True)
    financial_proposal_date = fields.Date(string="Financial Proposal Required On",related="lead_id.od_req_on_7",readonly=True)
    change_date = fields.Datetime(string="Latest Change Date",readonly=True)
    number = fields.Char(string='Number',default='/',readonly="1")
    reviewed_id = fields.Many2one('res.users',string='Owner',readonly=True,track_visibility='always')
    prepared_by = fields.Many2one('res.users',string='Prepared By',required="1",states={'draft':[('readonly',False)]},readonly=True,track_visibility='always')
    od_customer_id = fields.Many2one('res.partner',string='Customer',domain=[('customer','=',True),('is_company','=',True)],required=True,states={'draft':[('readonly',False)]},readonly=True,track_visibility='always')
    od_mat_sale_id = fields.Many2one('sale.order',string="Quotation",readonly=True,copy=False)
    od_ren_sale_id = fields.Many2one('sale.order',string="Quotation",readonly=True,copy=False)
    od_trn_sale_id = fields.Many2one('sale.order',string="Quotation",readonly=True,copy=False)
    od_bim_sale_id = fields.Many2one('sale.order',string="Quotation",readonly=True,copy=False)
    od_oim_sale_id = fields.Many2one('sale.order',string="Quotation",readonly=True,copy=False)
    od_bmn_sale_id = fields.Many2one('sale.order',string="Quotation",readonly=True,copy=False)
    od_omn_sale_id = fields.Many2one('sale.order',string="Quotation",readonly=True,copy=False)
    od_om_res_sale_id = fields.Many2one('sale.order',string="Quotation",readonly=True,copy=False)
    cost_summary_line = fields.One2many('od.cost.summary.line','cost_sheet_id',string='Cost Summary Line',help="Cost Summary",copy=True)
    cost_summary_manufacture_line = fields.One2many('od.cost.summary.manufacture.line','cost_sheet_id',string='Cost Summary Manufacture Line',states={'draft':[('readonly',False)]},readonly=True,copy=True)
    cost_summary_extra_line = fields.One2many('od.cost.summary.extra.line','cost_sheet_id',string='Cost Summary Extra Line',states={'draft':[('readonly',False)]},copy=True)
    cost_summary_version_line = fields.One2many('od.cost.summary.version.line','cost_sheet_id',string='Cost Summary Version Line',states={'draft':[('readonly',False)]},copy=True)
    payment_terms_line = fields.One2many('od.cost.terms.payment.terms.line','cost_sheet_id',string='Payment Terms Line',copy=True,states={'draft':[('readonly',False)]},default=default_payement_term_data)
    credit_terms_line = fields.One2many('od.cost.terms.credit.terms.line','cost_sheet_id',string='Creation Terms Line',copy=True,states={'draft':[('readonly',False)]})
    remarks1 = fields.Text('Remarks')
    remarks2 = fields.Text('Remarks')
    cost_section_line = fields.One2many('od.cost.section.line','cost_sheet_id',string='Cost Section Line',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,default=default_section_material)
    cost_section_option_line = fields.One2many('od.cost.opt.section.line','cost_sheet_id',string='Cost Section Line',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,default=default_section_optional)
    cost_section_trn_line = fields.One2many('od.cost.trn.section.line','cost_sheet_id',string='Cost Section Line',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,default=default_section_training)
    costgroup_it_service_line = fields.One2many('od.cost.costgroup.it.service.line','cost_sheet_id',string='Cost Costgroup It Service Line',copy=True,default=default_beta_service_line,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True)
    costgroup_material_line = fields.One2many('od.cost.costgroup.material.line','cost_sheet_id',string='Cost Costgroup Material Line',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,default=default_costgroup_material_line)
    costgroup_extra_expense_line = fields.One2many('od.cost.costgroup.extra.expense.line','cost_sheet_id',string='Cost Costgroup Material Line',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,default=default_costgroup_extra_expense_line)
    costgroup_optional_line = fields.One2many('od.cost.costgroup.optional.line.two','cost_sheet_id',string='Cost Costgroup Optional Line',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,default=default_costgroup_optional_line)
    mat_main_pro_line = fields.One2many('od.cost.mat.main.pro.line','cost_sheet_id',string='Mat Main Proposal Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    mat_optional_item_line = fields.One2many('od.cost.mat.optional.item.line','cost_sheet_id',string='Mat Optional Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    mat_brand_weight_line = fields.One2many('od.cost.mat.brand.weight','cost_sheet_id',string='Brand Weight',readonly=True)
    mat_group_weight_line = fields.One2many('od.cost.mat.group.weight','cost_sheet_id',string='Group Weight',readonly=True)
    imp_weight_line = fields.One2many('od.cost.impl.group.weight','cost_sheet_id',string='Implementation Weight',readonly=True)
    amc_weight_line = fields.One2many('od.cost.amc.group.weight','cost_sheet_id',string='Implementation Weight',readonly=True)
    om_weight_line = fields.One2many('od.cost.om.group.weight','cost_sheet_id',string='OM Weight',readonly=True)
    extra_weight_line = fields.One2many('od.cost.extra.group.weight','cost_sheet_id',string='Extra Weight',readonly=True)
    summary_weight_line = fields.One2many('od.cost.summary.group.weight','cost_sheet_id',string='Summary Weight',readonly=True)

    
    mat_extra_expense_line = fields.One2many('od.cost.mat.extra.expense.line','cost_sheet_id',string='Mat Extra Expense Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    show_to_customer_main_proposal = fields.Boolean(string='Show to Customer',default=True)
    show_to_opt = fields.Boolean(string='Show to Customer',default=False)
    show_mat_ext_exp =fields.Boolean(string='Show to Customer',default=False)
    show_to_customer_optional_proposal = fields.Boolean(string='Show to Customer',default=False)
    show_to_customer_mat_delivery = fields.Boolean(string='Show to Customer',default=True)
    show_to_customer_material_notes = fields.Boolean(string='Show to Customer',default=True)
    show_to_customer_bmn_eqp = fields.Boolean(string='Show to Customer',default=False)
    show_to_customer_omn_eqp = fields.Boolean(string='Show to Customer',default=False)
    show_to_customer_o_m_eqp = fields.Boolean(string='Show to Customer',default=False)
    show_to_customer_payment = fields.Boolean(string='Show to Customer',default=True)
    show_to_customer_credit = fields.Boolean(string='Show to Customer',default=False)
    material_delivery_terms = fields.Text(string='Material Delivery Terms',states={'draft':[('readonly',False)]},default="*Expected Delivery Period for Proposed Items is 4-6 Weeks\n* Default Warranty starts from the shipment date (from vendor factories) and not from installation date. Vendors Default warranty terms & conditions apply during this period. For extended warranty Terms & conditions, Vendors service contracts/certificates to be purchased. For Local Support, Beta IT Support Services should be purchased (such as Preventive Maintenance and Remedial Maintenance). \
\n* Electronic Licenses and Manufacturer Services will not be delivered as part of the material because they only represent codes which will be activated at the vendor site.")
    # material_notes = fields.Text(string='Material Notes',states={'draft':[('readonly',False)]},default="Expected Delivery Period for Proposed Items is 4-6 Weeks")
    included_in_quotation = fields.Boolean(string='Included In Quotation',default=False)
    ren_main_pro_line = fields.One2many('od.cost.ren.main.pro.line','cost_sheet_id',string='Ren Main Proposal Line',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True)
    ren_optional_item_line = fields.One2many('od.cost.ren.optional.item.line','cost_sheet_id',string='Ren Optional Line',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True)
    bmn_eqp_cov_line = fields.One2many('od.bmn.eqp.cov.line','cost_sheet_id',string='BMN Equipment Covered by The Scope of Service',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True)
    omn_eqp_cov_line = fields.One2many('od.omn.eqp.cov.line','cost_sheet_id',string='OMN Equipment Covered by The Scope of Service',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True)
    o_m_eqp_cov_line = fields.One2many('od.o_m.eqp.cov.line','cost_sheet_id',string='OM Equipment Covered by The Scope of Service',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True)
    bim_implementation_code_line = fields.One2many('od.cost.bim.beta.implementation.code','cost_sheet_id',string='Bim Implementation Code Line',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True)



    included_in_quotation_ren = fields.Boolean(string='Included In Quotation',default=False)
    renewal_quotes = fields.Html(string='Notes')
    show_to_customer_ren_main = fields.Boolean(string='Show to Customer',default=True)
    show_to_customer_ren_optional = fields.Boolean(string='Show to Customer',default=False)
    show_to_customer_ren_notes = fields.Boolean(string='Show to Customer',default=True)

    #trn
    trn_customer_training_line = fields.One2many('od.cost.trn.customer.training.line','cost_sheet_id',string='Trn Customer Training Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    # trn_customer_training_optional_line = fields.One2many('od.cost.trn.optional.line','cost_sheet_id',string='Trn Customer Optional Training Line',readonly=True, states={'draft':[('readonly',False)]})
    trn_customer_training_extra_expense_line = fields.One2many('od.cost.trn.customer.training.extra.expense.line','cost_sheet_id',string='Trn Customer Extra Expense Line',copy=True,states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True)
    included_trn_in_quotation = fields.Boolean(string='Included In Quotation',default=False)
    show_customer_trn_training_details = fields.Boolean(string='Show to Customer',default=True)
    show_customer_trn_terms_condition = fields.Boolean(string='Show to Customer',default=True)
    show_trn_training_extra_expenses = fields.Boolean(string='Show to Customer',default=False,states={'draft':[('readonly',False)]})
    trn_terms_condition = fields.Html(string='Terms And Condition',states={'draft':[('readonly',False)]},default="Training Provided does not cover examination fees and it does not include travelling & accommodation expenses if required.")

    #bim
    included_bim_in_quotation = fields.Boolean(string='Included In Quotation',default=False)
    show_customer_bim_exclusion = fields.Boolean(string='Show to Customer',default=True)
    show_customer_bim_manpower_calc = fields.Boolean(string='Show to Customer',default=False)
    bim_exclusion_note = fields.Html(string='Remarks',default=default_exclusion_note)
    show_customer_bim_inclusion = fields.Boolean(string='Show to Customer',default=True)
    show_bim_log_eqn = fields.Boolean(string='Show to Customer')
    show_bim_extra_exp = fields.Boolean(string='Show to Customer')
    show_imp_code = fields.Boolean(string='Show to Customer')
    show_oim_extra_exp = fields.Boolean(string='Show to Customer')
    bim_inclusion_note = fields.Html(string='Remarks',default=False)
    implimentation_extra_expense_line = fields.One2many('od.cost.bim.beta.implimentation.extra.expense.line','cost_sheet_id',string='Bim Extra Expense Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    manpower_manual_line = fields.One2many('od.cost.bim.beta.manpower.manual.line','cost_sheet_id',string='Bim Manpower Manual Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    #OIM
    included_oim_in_quotation = fields.Boolean(string='Included In Quotation',default=False)
    show_oim_ex_outsourced_scope = fields.Boolean(string='Show to Customer',default=True)
    oim_ex_outsourced_scope = fields.Text(string='Remarks',default=False)
    show_oim_in_outsourced_scope = fields.Boolean(string='Show to Customer',default=True)
    oim_in_outsourced_scope = fields.Text(string='Remarks',default=False)
    show_oim_outsourced_price = fields.Boolean(string='Show to Customer',default=False)
    oim_implimentation_price_line = fields.One2many('od.cost.oim.implimentation.price.line','cost_sheet_id',string='Oim Implimentation Price Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    oim_extra_expenses_line = fields.One2many('od.cost.oim.extra.expenses.line','cost_sheet_id',string='Oim Extra Expense Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    #o&m
    included_om_in_quotation = fields.Boolean(string='Included In Quotation',default=False)
    show_om_residenteng_cust = fields.Boolean(string='Show to Customer')
    om_residenteng_line = fields.One2many('od.cost.om.residenteng.line','cost_sheet_id',string='Om Resident Eng Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True,default=default_resident_eng_line)
    show_om_eqpmntreqst_cust = fields.Boolean(string='Show to Customer',default=False)
    om_eqpmentreq_line = fields.One2many('od.cost.om.eqpmentreq.line','cost_sheet_id',string='Om Equipment Request Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    show_om_exclusion_cust = fields.Boolean(string='Show to Customer',default=True)
    om_ex_works_note = fields.Html(string='Remarks',default=False)
    show_om_extra_exp = fields.Boolean(string='Show to Customer')
    show_om_inclusion_cust = fields.Boolean(string='Show to Customer',default=True)
    om_in_works_note = fields.Html(string='Remarks',default=False)
    om_extra_line = fields.One2many('od.cost.om.extra.line','cost_sheet_id',string='Om Extra Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    #OMN
    included_omn_in_quotation = fields.Boolean(string='Included In Quotation',default=False)
    show_to_cust_omn_maintanance = fields.Boolean(string='Show to Customer',default=False)

    omn_level = fields.Char(string='Level')
    omn_year_month = fields.Selection([('week','Week'),('month','Month'),('year','Year')],'Week, Month or Year') #FA
    omn_number = fields.Integer('Number')
    omn_public_holiday = fields.Boolean('Public Holidays')
    omn_start_date = fields.Date('Omn Start Date')
    omn_end_date = fields.Date('Omn End Date')
    omn_comment = fields.Char('Omn Comment')
    #O_M
    o_m_level = fields.Char(string='Level')
    o_m_year_month = fields.Selection([('week','Week'),('month','Month'),('year','Year')],'Week, Month or Year') #FA
    o_m_number = fields.Integer('Number')
    o_m_public_holiday = fields.Boolean('Public Holidays')
    o_m_start_date = fields.Date('Om Start Date')
    o_m_end_date = fields.Date('Om End Date')
    o_m_comment = fields.Char('Om Comment')
#     omn_year = fields.Selection([(num, str(num)) for num in range(1990, (datetime.now().year)+1 )], 'Year')
    show_to_cust_omn_maintance_price = fields.Boolean(string='Show to Customer',default=False)
    omn_out_preventive_maintenance_line = fields.One2many('od.cost.omn.out.preventive.maintenance.line','cost_sheet_id',string='Omn Preventive Maintenance Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True,default=default_omn_preventive_line)
    show_to_cust_omn_remedial_maintenance = fields.Boolean(string='Show to Customer',default=False)
    omn_out_remedial_maintenance_line = fields.One2many('od.cost.omn.out.remedial.maintenance.line','cost_sheet_id',string='Omn Remedial Maintenance Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True,default=default_omn_remedial_line)
    show_to_cust_remarks = fields.Boolean(string='Show to Customer',default=True)
    omn_remarks = fields.Text(string='Remarks',default="* Devices covered by Beta IT maintenance services must be covered by valid manufacturer warranty & TAC support\n\n* Level 1 Support - Customer Responsibility (Problem Reporting and Basic Information)\n* Level 2 Support - Beta IT Responsibility (Troubleshooting and Workaround)\n* Level 3 Support - Beta IT / Manufacturer Responsibility (Root Cause Analysis)\n* Level 4 Support - Manufacturer Responsibility (Root access, Engineering, and Development)\n* Warranty - Devices covered by this service must be covered by manufacturer warranty: Beta IT will process RMA process on behalf of customer for malfunctioning devices provided that customer has a valid support contract with manufacturer and as per manufacturer terms and conditions. Material, covered by manufacturer warranty services, is subject to manufacturer warranty and RMA policies, procedures, and RMA repair periods. RMA and Manufactures' support conditions are provided by each manufacturer on its own web site.\n* Fault Classification / Response Times:\n\t\tA. Critical (service affecting) - Response Means: Phone & Email (One Business Hour), Response Means: Remote Access (2 Business Hours), Response Means: On-Site (4 Business Hours + Travelling Time)\n\t\tB. Major (service affecting): Response Means: Phone & Email (One Business Hour), Response Means: Remote Access (4 Business Hours), Response Means: On-Site (7 Business Hours + Travelling Time)\n\t\tC. Minor (non-service affecting): Response Means: Phone & Email (24 Business Hour), Response Means: Remote Access (48 Business Hours), Response Means: On-Site (72 Business Hours + Travelling Time)\n\n* Escalation Sequence / Matrix\n\t\tLevel A. Beta IT Helpdesk (United Arab Emirates: +971 4 250 0111 support@betait.net / Saudi Arabia: 920006069 support@sa.betait.net)\n\t\tLevel B. Beta IT Technical Department (United Arab Emirates:  +971 4 706 1111 td@betait.net / Saudi Arabia: +966 11 200 6066 td@sa.betait.net)\n\t\tLevel C. Head of Operations (United Arab Emirates:  +971 4 706 1111 mohd.elayyan@betait.net / Saudi Arabia: +966 11 200 6066 fakhri.amaireh@sa.betait.net) ")
    show_to_cust_spare_parts = fields.Boolean(string='Show to Customer',default=False)
    omn_spare_parts_line = fields.One2many('od.cost.omn.spare.parts.line','cost_sheet_id',string='Omn Spare Parts Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    omn_maintenance_extra_expense_line = fields.One2many('od.cost.omn.maintenance.extra.expense.line','cost_sheet_id',string='Omn Extra Expense Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    #BMN
    included_bmn_in_quotation = fields.Boolean(string='Included In Quotation',default=False)
    show_to_cust_bmn_maintanance = fields.Boolean(string='Show to Customer',default=False)


    bmn_level = fields.Char(string='Level')
    bmn_year_month = fields.Selection([('week','Week'),('month','Month'),('year','Year')],'Week, Month or Year') #FA
    bmn_public_holiday = fields.Boolean('Public Holidays')
    bmn_number = fields.Integer('Number')
    bmn_start_date = fields.Date('Bmn Start Date')
    bmn_end_date = fields.Date('Bmn End Date')
    bmn_comment = fields.Char('Bmn Comment')
#     bmn_year = fields.Selection([(num, str(num)) for num in range(1990, (datetime.now().year)+1 )], 'Year')
    show_bmn_it_preventive_line = fields.Boolean(string='Show to Customer',default=False)
    bmn_it_preventive_line = fields.One2many('od.cost.bmn.it.preventive.line','cost_sheet_id',string='Bmn It Preventive Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True,default=default_bmn_it_preventive_line)
    show_bmn_it_remedial_line = fields.Boolean(string='Show to Customer',default=False)
    bmn_it_remedial_line = fields.One2many('od.cost.bmn.it.remedial.line','cost_sheet_id',string='Bmn It Remedial Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True,default=default_bmn_it_remedial_line)
    show_bmn_scope_maintanance = fields.Boolean(string='Show to Customer',default=True)
    bmn_beta_it_maintanance = fields.Html(string='Remarks',default=default_amc_scope)
    show_to_cust_bmn_beta_spareparts = fields.Boolean(string='Show to Customer',default=False)
    bmn_spareparts_beta_it_maintenance_line = fields.One2many('od.cost.bmn.spareparts.beta.it.maintenance.line','cost_sheet_id',string='Bmn Spareparts Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    bmn_beta_it_maintenance_extra_expense_line = fields.One2many('od.cost.bmn.beta.it.maintenance.extra.expense.line','cost_sheet_id',string='Bmn Extra Expense Line',states={'draft':[('readonly',False)],'design_ready':[('readonly',False)],'submitted':[('readonly',False)],'returned_by_pmo':[('readonly',False)],'returned_by_fin':[('readonly',False)],'handover':[('readonly',False)],'change':[('readonly',False)],'modify':[('readonly',False)]},readonly=True,copy=True)
    # customer_closing_line = fields.One2many('od.customer.closing.line','cost_sheet_id',string='Customer Closing Condition Line',copy=True,states={'draft':[('readonly',False)],'submitted':[('readonly',False)],'handover':[('readonly',False)],'processed':[('readonly',False)]},readonly=True)
    # beta_closing_line = fields.One2many('od.beta.closing.line','cost_sheet_id',string='Customer Closing Condition Line',copy=True,states={'draft':[('readonly',False)],'submitted':[('readonly',False)],'handover':[('readonly',False)],'processed':[('readonly',False)]},readonly=True)
    closing_condition_ids = fields.Many2many('od.beta.closing.conditions','rel_costsheet_condition','costsheet_id','condition_id',string="Closing Conditions")
    closing_fin_comment_id  = fields.Many2one('od.finance.comment','Finance Comment')
    od_order_type_id = fields.Many2one('od.order.type',string='Order Type',domain=[('type','=','so')])
    type_mat = fields.Many2one('od.order.type',string='Order Type',domain=[('type','=','so')])
    type_ren = fields.Many2one('od.order.type',string='Order Type',domain=[('type','=','so')])
    type_trn = fields.Many2one('od.order.type',string='Order Type',domain=[('type','=','so')])
    type_bim = fields.Many2one('od.order.type',string='Order Type',domain=[('type','=','so')])
    type_oim = fields.Many2one('od.order.type',string='Order Type',domain=[('type','=','so')])
    type_bmn = fields.Many2one('od.order.type',string='Order Type',domain=[('type','=','so')])
    type_omn = fields.Many2one('od.order.type',string='Order Type',domain=[('type','=','so')])
    type_o_m = fields.Many2one('od.order.type',string='Order Type',domain=[('type','=','so')])

#project fields

    project_mat  = fields.Many2one('account.analytic.account',string='Project',domain=[('type','=','contract'),('state','=','open')])
    project_ren  = fields.Many2one('account.analytic.account',string='Project',domain=[('type','=','contract'),('state','=','open')])
    project_trn  = fields.Many2one('account.analytic.account',string='Project',domain=[('type','=','contract'),('state','=','open')])
    project_bim  = fields.Many2one('account.analytic.account',string='Project',domain=[('type','=','contract'),('state','=','open')])
    project_oim  = fields.Many2one('account.analytic.account',string='Project',domain=[('type','=','contract'),('state','=','open')])
    project_bmn  = fields.Many2one('account.analytic.account',string='Project',domain=[('type','=','contract'),('state','=','open')])
    project_omn  = fields.Many2one('account.analytic.account',string='Project',domain=[('type','=','contract'),('state','=','open')])
    project_o_m  = fields.Many2one('account.analytic.account',string='Project',domain=[('type','=','contract'),('state','=','open')])
    
    price_fixed = fields.Boolean(string="Price Fixed")
    
    def get_analytic_state(self):
        return      [             
             ('template', 'Template'),
             ('draft','New'),
             ('open','In Progress'),
            ('pending','To Renew'),
             ('close','Closed'),
            ('cancelled', 'Cancelled')
                    ]

 #Related Analytic_state
    
    
    
    project_mat_state  = fields.Selection(get_analytic_state,string='Mat Analtyic State',related="project_mat.state" ,readonlyt=True)
    project_ren_state  = fields.Selection(get_analytic_state,string='Ren Analtyic State',related="project_ren.state",readonlyt=True)
    project_trn_state  = fields.Selection(get_analytic_state,string='Trn Analtyic State',related="project_trn.state",readonlyt=True)
    project_bim_state  = fields.Selection(get_analytic_state,string='Bim Analtyic State',related="project_bim.state",readonlyt=True)
    project_oim_state  = fields.Selection(get_analytic_state,string='Oim Analtyic State',related="project_oim.state",readonlyt=True)
    project_bmn_state  = fields.Selection(get_analytic_state,string='Bmn Analtyic State',related="project_bmn.state",readonlyt=True)
    project_omn_state  = fields.Selection(get_analytic_state,string='Omn Analtyic State',related="project_omn.state",readonlyt=True)
    project_o_m_state  = fields.Selection(get_analytic_state,string='OM Analtyic State',related="project_o_m.state",readonlyt=True)

# fields for comm
    comm_made_to_customer = fields.Text('Commitments I Made Customer or Suppliers')
    # comm_made_to_me = fields.Text('Commitments Made to Me by Customer or Suppliers')





    @api.model
    def create(self,vals):
        lead_id = self.env.context.get('default_lead_id')
        if lead_id:
            if vals.get('status') == 'active':
                old_cost_sheets = self.search([('status','=','active'),('lead_id','=',lead_id)])
                if len(old_cost_sheets) > 0:
                    raise Warning('Active Cost Sheet for Each Lead Must Be Unique')
        if vals.get('number','/')=='/':
            vals['number'] = self.env['ir.sequence'].get('od.cost.sheet') or '/'

        return super(od_cost_sheet, self).create( vals)

    @api.multi
    def write(self,vals):

        if vals.get('status') == 'active':
            lead_id = self.lead_id and self.lead_id.id
            old_cost_sheets = self.search([('status','=','active'),('lead_id','=',lead_id)])
            if len(old_cost_sheets) > 0:
                raise Warning('Active Cost Sheet for Each Lead Must Be Unique')
        return super(od_cost_sheet,self).write(vals)
    @api.one
    def recalculate(self):
        for line in self.mat_main_pro_line:
            line._compute_currency_supp_discount()
            line._compute_supplier_discount()
            line._compute_unit_price()
#             line.onchange_vat()
        for line in self.trn_customer_training_line:
            line._compute_currency_supp_discount()
            line._compute_supplier_discount()
            line._compute_unit_price()
#             line.onchange_vat()


    def check_order_type(self):
        if not self.included_in_quotation:
            raise Warning("MAT tab Included In Quotation Not Ticked")
        if not self.type_mat.id:
            raise Warning("MAT tab Order Type Not Selected")
        if not self.project_mat:
            raise Warning("MAT tab Project Not Selected")

    def map_analytic_acc(self,anal_dict):
        res = {}
        result = {}
        for key,value in anal_dict.iteritems():
            res.setdefault(value,[]).append(key)
        for key,value in res.iteritems():
            if key:
                result[key] = value
        return result

    def sum_grouped_pdt(self,result):
        res = []
        for vals in result:
            prices =sum(vals['prices'])
            costs =sum(vals['costs'])
            qty = sum(vals['quants'])
            sup_prices = sum(vals['sup_prices'])
            unit_sup_price = sup_prices/(qty or 1.0)
            unit_price = prices/qty
            unit_cost = costs/qty
            vals['product_uom_qty'] = qty
            vals['od_original_qty'] = qty
            vals['price_unit'] = unit_price
            vals['od_original_price'] = unit_price
            vals['purchase_price'] = unit_cost
            vals['od_original_unit_cost'] = unit_cost
            vals['od_sup_unit_cost'] =unit_sup_price
            vals['od_sup_line_cost'] =sup_prices
            if vals.get('tax_id') == [[6,False,[False]]]:
                vals['tax_id'] = False
            res.append((0,0,vals))
        return res

    def od_deduplicate_pdt(self,l):
        '''
        group same products  to single items,price_unit sum and and divid by qty
         '''
        result = []
        for _,_,item in l :
            check = False
            for r_item in result :
                if item['product_id'] == r_item['product_id'] :
                    check = True
                    sup_prices = r_item['sup_prices']
                    sup_prices.append(item['od_sup_unit_cost'] * item['product_uom_qty'])
                    prices = r_item['prices']
                    prices.append(item['price_unit']*item['product_uom_qty'])
                    r_item['prices'] =prices
                    costs = r_item['costs']
                    costs.append(item['purchase_price']*item['product_uom_qty'])
                    r_item['costs'] = costs
                    quants = r_item['quants']
                    quants.append(item['product_uom_qty'])
                    r_item['quants'] = quants
            if check == False :
                item['prices'] = [item['price_unit'] * item['product_uom_qty']]
                item['costs'] = [item['purchase_price']  * item['product_uom_qty']]
                item['quants'] =[item['product_uom_qty']]
                item['sup_prices'] = [item['od_sup_unit_cost'] * item['product_uom_qty']]
                result.append( item )
        result = self.sum_grouped_pdt(result)
        return result


    def get_so_tab_map(self):
        so_analyti_map = {}
        od_mat_sale_id =  self.od_mat_sale_id and self.od_mat_sale_id.id or False
        if od_mat_sale_id:
            mat_analytic = self.od_mat_sale_id and self.od_mat_sale_id.project_id and self.od_mat_sale_id.project_id.id
            so_analyti_map[od_mat_sale_id] = mat_analytic
        od_trn_sale_id =  self.od_trn_sale_id and self.od_trn_sale_id.id or False
        if od_trn_sale_id:
            trn_analytic = self.od_trn_sale_id and self.od_trn_sale_id.project_id and self.od_trn_sale_id.project_id.id
            so_analyti_map[od_trn_sale_id] = trn_analytic
        od_bim_sale_id =  self.od_bim_sale_id and self.od_bim_sale_id.id or False
        if od_bim_sale_id:
            imp_analytic = self.od_bim_sale_id and self.od_bim_sale_id.project_id and self.od_bim_sale_id.project_id.id
            so_analyti_map[od_bim_sale_id] = imp_analytic
        od_bmn_sale_id =  self.od_bmn_sale_id and self.od_bmn_sale_id.id or False
        if od_bmn_sale_id:
            amc_analytic = self.od_bmn_sale_id and self.od_bmn_sale_id.project_id and self.od_bmn_sale_id.project_id.id
            so_analyti_map[od_bmn_sale_id] = amc_analytic
        od_om_res_sale_id = self.od_om_res_sale_id and self.od_om_res_sale_id.id or False
        if od_om_res_sale_id:
            o_m_analytic = self.od_om_res_sale_id and self.od_om_res_sale_id.project_id and self.od_om_res_sale_id.project_id.id
            so_analyti_map[od_om_res_sale_id] = o_m_analytic
        so_tab_map = {'mat':od_mat_sale_id,'trn':od_trn_sale_id,'imp':od_bim_sale_id,'amc':od_bmn_sale_id,'o_m':od_om_res_sale_id}
        return so_tab_map,so_analyti_map

    def update_tab_sale_order_link(self,new_tab_so_map):
        for tab,so_id in new_tab_so_map.iteritems():
            if tab == 'mat':
                self.od_mat_sale_id = so_id
            elif tab == 'trn':
                self.od_trn_sale_id = so_id
            elif tab == 'imp':
                self.od_bim_sale_id = so_id
            elif tab == 'amc':
                self.od_bmn_sale_id = so_id
            elif tab == 'o_m':
                self.od_om_res_sale_id = so_id
    def write_sale_order_line(self,sale_id,order_vals):
        # print "order vals>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",order_vals
        sale_line = self.env['sale.order.line']
        old_lines = sale_id.order_line
        current_line = self.env['sale.order.line']
        # pprint(order_vals)
        discount = self.special_discount
        sale_id.write({'od_discount':discount})
        for _,_,line in order_vals:
            sale_order_line = sale_line.search([('order_id','=',sale_id.id),('product_id','=',line.get('product_id')),('od_inactive','=',False)])
            if sale_order_line:
                sale_order_line.write({
                    'product_uom_qty':line.get('product_uom_qty'),
                    'price_unit':line.get('price_unit'),
                    'purchase_price':line.get('purchase_price'),
                    'od_sup_unit_cost':line.get('od_sup_unit_cost'),
                    'od_sup_line_cost':line.get('od_sup_unit_cost',0) *line.get('product_uom_qty',0),
                     'tax_id':line.get('tax_id',[[6,False,[]]]),
                    
                })
                current_line |= sale_order_line
            else:
                line.update({'order_id':sale_id.id,'od_original_price':0.0,'od_original_qty':0.0,'od_original_unit_cost':0.0})
                sale_line.create(line)
        (old_lines - current_line).write({'product_uom_qty':0,'price_unit':0.0,'purchase_price':0.0,'od_inactive':True})

    def write_analytic_map_sale_order(self,anal_maped_dict,so_vals,so_line_map):
        od_discount = so_vals.get('od_discount',0)
        new_sale_ob = False
        if od_discount:
            discount = od_discount
#             so_line_map = self.apply_discount_write(so_line_map,discount)
        new_analytic_so_map = {}
        second_analytic_so_map = {}
        new_tab_so_map ={}
        so_need_to_update = []
        sale_line_pool = self.env['sale.order.line']
        sale_pool = self.env['sale.order']
        analytic = self.env['account.analytic.account']
        so_tab_map,so_analyti_map = self.get_so_tab_map()
        analytic_so_map = {v: k for k, v in so_analyti_map.items()}
        for analytic_id,tabs in anal_maped_dict.iteritems():
            print "tabs>>>>>>>>>>>>>>>>>>>>>>>>,analytic_id",tabs,analytic_id
            so_vals['project_id'] = analytic_id
            so_vals['name'] = '/'
            order_line = []
            for tab in tabs:
                order_line += so_line_map[tab]
                print "order line>>>>>>>>>>>>",order_line
            order_line = self.od_deduplicate_pdt(order_line)
            for tab in tabs:
                so_id = so_tab_map.get(tab,False)
                if so_id:
                    so_analytic_id =so_analyti_map.get(so_id,False)
                    if so_analytic_id and so_analytic_id != analytic_id:
                        sale_lines = sale_line_pool.search([('order_id','=',so_id),('od_tab_type','=',tab)])
                        if not sale_lines:
                            raise Warning("Tab Type Not Linked in Sale Order With Id = %s"%so_id)
                        new_sale_id = analytic_so_map.get(analytic_id,False)
                        if not new_sale_id:
                            new_sale_id = new_analytic_so_map.get(analytic_id,False)
                        if not new_sale_id:
                            new_sale_id = sale_pool.create(so_vals)
                            print "new sale id>>>>>>>>>>>>>>>>>",new_sale_id
                            new_sale_ob = new_sale_id
#                             new_sale_id.od_action_approve()
                            new_sale_id = new_sale_id.id
                            new_analytic_so_map[analytic_id] = new_sale_id
                        sale_lines.write({'order_id':new_sale_id})
                        if new_sale_ob:
                            new_sale_ob.od_action_approve()
                        new_tab_so_map[tab] = new_sale_id
                        so_need_to_update.append(new_sale_id)
                    else:
                        so_need_to_update.append(so_id)
                        # self.write_sale_order_line(sale_id,order_line)
                else:
                    so_id = analytic_so_map.get(analytic_id,False)
                    if not so_id:

                        so_vals['order_line'] = order_line
                        so_id = self.env['sale.order'].create(so_vals)
                        so_id.od_action_approve()
                        so_id = so_id.id
                        analytic_so_map[analytic_id] = so_id
                    new_tab_so_map[tab] = so_id

            so_need_to_update = list(set(so_need_to_update))
            if so_need_to_update:
                for so in so_need_to_update:
                    sale_id = sale_pool.browse(so)
                    self.write_sale_order_line(sale_id,order_line)
                    so_need_to_update.remove(so)
            if new_tab_so_map:
                self.update_tab_sale_order_link(new_tab_so_map)




    def create_analytic_map_sale_order(self,anal_maped_dict,so_vals,so_line_map):
        od_discount = so_vals.get('od_discount',0)
#         if od_discount:
#             discount = od_discount
#             so_line_map = self.apply_discount_create(so_line_map,discount)
        analytic = self.env['account.analytic.account']
        for analytic_id,tabs in anal_maped_dict.iteritems():
            so_vals['project_id'] = analytic_id
            analytic_ob = analytic.browse(analytic_id)
            analytic_ob.write({'od_cost_sheet_id':self.id})
            order_line = []
            for tab in tabs:
                order_line += so_line_map[tab]
            order_line = self.od_deduplicate_pdt(order_line)
            # pprint(order_line)
            if not order_line:
                raise Warning("No Order Line to Create Sale Order")
            so_vals['order_line'] =  order_line
            so_vals['name'] = '/'
            company_id = self.company_id and self.company_id.id
            so_vals['company_id'] =company_id
            # sdfsfsfs
            pprint(so_vals)
            so_id = self.env['sale.order'].create(so_vals)
            so_id.od_action_approve()
            for tab in tabs:
                if tab == 'mat':
                    if not self.od_mat_sale_id:
                        self.od_mat_sale_id = so_id.id
                elif tab == 'imp':
                    if not self.od_bim_sale_id:
                        self.od_bim_sale_id = so_id.id

                elif tab == 'o_m':
                    if not self.od_om_res_sale_id:
                        self.od_om_res_sale_id = so_id.id
                elif tab == 'trn':
                    if not self.od_trn_sale_id:
                        self.od_trn_sale_id = so_id.id
                elif tab == 'amc':
                    if not self.od_bmn_sale_id:
                        self.od_bmn_sale_id = so_id.id
        return True

    def get_product_id_from_param(self,product_param):
        parameter_obj = self.env['ir.config_parameter']
        key =[('key', '=', product_param)]
        product_param_obj = parameter_obj.search(key)
        if not product_param_obj:
            raise Warning(_('Settings Warning!'),_('NoParameter Not defined\nconfig it in System Parameters with %s'%product_param))
        product_id = product_param_obj.od_model_id and product_param_obj.od_model_id.id or False
        return product_id


    def get_product_name(self,product_id):
        product = self.env['product.product']
        product_obj = product.browse(product_id)
        return product_obj.description_sale or product_obj.name
    def get_product_brand(self,product_id):
        product = self.env['product.product']
        product_obj = product.browse(product_id)
        return product_obj.od_pdt_brand_id and product_obj.od_pdt_brand_id.id or False
    
    def get_product_tax(self):
        ksa = self.is_saudi_comp()
        param ='default_product_tax'
        if ksa:
            param =param+'_saudi'
        parameter_obj = self.env['ir.config_parameter']
        key =[('key', '=', param)]
        tax_param_obj = parameter_obj.search(key)
        if not tax_param_obj:
            raise Warning(_('Settings Warning!'),_('NoParameter Not defined\nconfig it in System Parameters with %s'%key))

        
        return tax_param_obj.od_model_id and tax_param_obj.od_model_id.id or False


    def apply_discount_create(self,so_line_map,discount):
        all_sale_order_line = []
        total_selling_price = 0.0
        for key,val in so_line_map.iteritems():
            all_sale_order_line += val
        for _,_,item in all_sale_order_line:
            price = item.get('price_unit',0.0)
            qty = item.get('product_uom_qty',0.0)
            total_selling_price += price * qty
        for key,val in so_line_map.iteritems():
            for _,_,res in val:
                price_unit = res.get('price_unit',0.0)
                discount_to_apply = 0
                if total_selling_price:
                    discount_to_apply = (price_unit/total_selling_price)*discount
                new_price = price_unit + discount_to_apply
                res['price_unit'] = new_price
                res['od_original_price'] = new_price
        return so_line_map
    def apply_discount_write(self,so_line_map,discount):
        all_sale_order_line = []
        total_selling_price = 0.0
        for key,val in so_line_map.iteritems():
            all_sale_order_line += val
        for _,_,item in all_sale_order_line:
            price = item.get('price_unit',0.0)
            qty = item.get('product_uom_qty',0.0)
            total_selling_price += price * qty
        for key,val in so_line_map.iteritems():
            for _,_,res in val:
                price_unit = res.get('price_unit',0.0)
                discount_to_apply = 0
                if total_selling_price:
                    discount_to_apply = (price_unit/total_selling_price)*discount
                new_price = price_unit + discount_to_apply
                res['price_unit'] = new_price
        return so_line_map


    @api.one
    def generate_sale_order(self):
        # self.check_order_type()
#         material_line_pool = self.env['od.cost.mat.main.pro.line']
        customer_id = self.od_customer_id.id
#         project_id = self.project_id and self.project_id.id or False
#         order_type = self.order_type and self.order_type.id or False
#         if not project_id:
#             raise Warning('No Project Selected')
#         if not order_type:
#             raise Warning('No Order Type Selected')

        default_svat = self.get_product_tax()
        tsvat = [[6,False,[default_svat]]] 

        bdm_user_id = self.lead_id and self.lead_id.od_bdm_user_id and self.lead_id.od_bdm_user_id.id or False
        presale_user_id = self.lead_id and self.lead_id.od_responsible_id and self.lead_id.od_responsible_id.id or False

        type_mat = self.type_mat.id
        type_ren = self.type_ren.id
        type_bim = self.type_bim.id
        type_oim = self.type_oim.id
        type_omn = self.type_omn.id
        type_o_m = self.type_o_m.id
        type_trn = self.type_trn.id
        type_bmn = self.type_bmn.id

        project_mat = self.project_mat and self.project_mat.id
        project_ren = self.project_ren and self.project_ren.id
        project_bim = self.project_bim and self.project_bim.id
        project_oim = self.project_oim and self.project_oim.id
        project_omn = self.project_omn and self.project_omn.id
        project_o_m = self.project_o_m and self.project_o_m.id
        project_trn = self.project_trn and self.project_trn.id
        project_bmn = self.project_bmn and self.project_bmn.id

        material_lines = []
        b_lines = []
        o_lines = []
        om_lines = []
        om_r_lines = []
        trn_lines = []
        bm_lines = []

        anal_dict = {'mat':project_mat,'imp':project_bim,'oim':project_oim,'omn':project_omn,'o_m':project_o_m,'trn':project_trn,'amc':project_bmn}

        #mat sales
        if self.included_in_quotation:
            if not project_mat:
                raise Warning("Analytic Account Not Selected In MAT Tab, Which is Enabled Included In Quotation,Please Select It")
            material_lines =[]
            mat_expense = 0.0
            mat_ext_sale = 0.0
            for line in self.mat_main_pro_line:
                material_lines.append((0,0,{
                                            'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                             'product_id':line.part_no.id,
                                             'name':line.part_no.description_sale or line.part_no.name,
                                             'od_original_qty':line.qty,
                                             'od_original_price':line.unit_price,
                                             'od_original_unit_cost':line.unit_cost_local,
                                             'product_uom_qty':line.qty,
                                             'price_unit':line.unit_price,
                                             'purchase_price':line.unit_cost_local,
                                             'od_analytic_acc_id':project_mat,
                                             'od_cost_sheet_id':self.id,
                                             'od_tab_type':'mat',
                                             'od_sup_unit_cost':line.discounted_unit_supplier_currency,
                                             'od_sup_line_cost':line.discounted_total_supplier_currency,
                                             'tax_id':[[6,False,[line.tax_id.id]]] 
                                             }))
                
                    

            for line in self.mat_extra_expense_line:
                mat_expense += line.qty * line.unit_cost_local
                mat_ext_sale += line.qty * line.unit_price2
            mat_exp_product_id = self.get_product_id_from_param('product_mat_extra_expense')
            material_lines.append((0,0,{
                                    'name':self.get_product_name(mat_exp_product_id),
                                    'od_manufacture_id':self.get_product_brand(mat_exp_product_id),
                                    'product_id':mat_exp_product_id,
                                    'product_uom_qty':1,
                                    'price_unit':mat_ext_sale,
                                     'od_original_qty':1,
                                     'od_original_unit_cost':mat_expense,
                                     'purchase_price':mat_expense,
                                     'od_original_price':mat_ext_sale,
                                      'od_cost_sheet_id':self.id,
                                      'od_tab_type':'mat',
                                     'od_analytic_acc_id':project_mat,
                                     'tax_id':tsvat,
#                                      'tax_id':[[6,False,[line.tax_id.id]]],
                                     'od_sup_unit_cost':0,
                                            
                                    }))
            if not material_lines:
                raise Warning('NO lines to Create Quotation for MAT Tab')

        # Training Sale Order
        if self.included_trn_in_quotation:

            trn_lines =[]
            trn_expense = 0.0
            trn_extra_sale = 0.0
            for line in self.trn_customer_training_line:
                if not project_trn:
                    raise Warning("Analytic Account Not Selected In TRN Tab, Which is Enabled Included In Quotation,Please Select It")
                trn_lines.append((0,0,{
                                            'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                             'product_id':line.part_no.id,
                                               'name':line.part_no.description_sale or line.part_no.name,
                                              'od_original_qty':line.qty,
                                              'od_original_price':line.unit_price,
                                              'od_original_unit_cost':line.unit_cost_local,
                                              'purchase_price':line.unit_cost_local,
                                              'product_uom_qty':line.qty,
                                              'price_unit':line.unit_price,
                                               'od_cost_sheet_id':self.id,
                                                'od_tab_type':'trn',
                                              'od_analytic_acc_id':project_trn,
                                              'tax_id':[[6,False,[line.tax_id.id]]],
                                               'od_sup_unit_cost':line.discounted_unit_supplier_currency,
                                             'od_sup_line_cost':line.discounted_total_supplier_currency,
                                             }))
            for line in self.trn_customer_training_extra_expense_line:
                trn_expense += line.qty * line.unit_cost_local
                trn_extra_sale += line.qty * line.unit_price2
            trn_exp_product_id = self.get_product_id_from_param('product_trn_extra_expense')
            trn_lines.append((0,0,{
                                    'name':self.get_product_name(trn_exp_product_id),
                                    'od_manufacture_id':self.get_product_brand(trn_exp_product_id),
                                    'product_id':trn_exp_product_id,
                                    'product_uom_qty':1,
                                     'od_original_qty':1,
                                     'od_original_price':trn_extra_sale,
                                     'od_original_unit_cost':trn_expense,
                                     'purchase_price':trn_expense,
                                    'price_unit':trn_extra_sale,
                                     'od_cost_sheet_id':self.id,
                                     'od_tab_type':'trn',
                                      'tax_id':tsvat,
#                                      'tax_id':[[6,False,[line.tax_id.id]]],
                                    'od_analytic_acc_id':project_trn,
                                    'od_sup_unit_cost':0,
                                    
                                }))

            if not trn_lines:
                raise Warning('NO lines to Create Quotation TRN Tab')

#         Bim sale order generation #Now Imp tab

        bi_ext_exp = 0.0
        bi_ext_exp_cost = 0.0
        bim_price = bim_cost= 0
        b_lines = []
        oim_price = 0.0
        oim_cost  = 0.0
        oim_exp= 0.0
        oim_exp_cost = 0.0
        if self.bim_log_select:
            bim_price = self.bim_log_price
            bim_cost = self.bim_log_cost
        if self.included_bim_in_quotation:
            if not project_bim:
                raise Warning("Analytic Account Not Selected In IMP Tab, Which is Enabled Included In Quotation,Please Select It")

            for oim_line in self.oim_extra_expenses_line:
                oim_exp += oim_line.qty * oim_line.unit_price
                oim_exp_cost += oim_line.qty * oim_line.unit_cost
            oim_exp_product_id = self.get_product_id_from_param('product_oim_extra_expense')
            b_lines.append((0,0,{'name':self.get_product_name(oim_exp_product_id),
                                'product_id':oim_exp_product_id,
                                'od_manufacture_id':self.get_product_brand(oim_exp_product_id),
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':oim_exp,
                                'od_original_unit_cost':oim_exp_cost,
                                'purchase_price':oim_exp_cost,
                                'price_unit':oim_exp,
                                'od_cost_sheet_id':self.id,
                                'od_tab_type':'imp',
                                'od_analytic_acc_id':project_bim,
                                'tax_id':tsvat,
                                
#                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                'od_sup_unit_cost':0,
                                }))
            for oim_line in self.oim_implimentation_price_line:
                oim_price += oim_line.qty * oim_line.unit_price
                oim_cost += oim_line.qty * oim_line.unit_cost
            oim_product_id = self.get_product_id_from_param('product_oim')
            b_lines.append((0,0,{'name':self.get_product_name(oim_product_id),
                                'od_manufacture_id':self.get_product_brand(oim_product_id),
                                'product_id':oim_product_id,
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':oim_price,
                                'od_original_unit_cost':oim_cost,
                                'purchase_price':oim_cost,
                                'price_unit':oim_price,
                                'od_cost_sheet_id':self.id,
                                'tax_id':tsvat,
#                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                'od_tab_type':'imp',
                                'od_analytic_acc_id':project_bim,
                                'od_sup_unit_cost':0,
                                }))


            for bim_line in self.implimentation_extra_expense_line:
                bi_ext_exp += bim_line.qty * bim_line.unit_price
                bi_ext_exp_cost +=  bim_line.qty * bim_line.unit_cost
            bim_exp_product_id = self.get_product_id_from_param('product_bim_extra_expense')
            b_lines.append((0,0,{
                            'name':self.get_product_name(bim_exp_product_id),
                            'od_manufacture_id':self.get_product_brand(bim_exp_product_id),
                            'product_id':bim_exp_product_id,
                            'product_uom_qty':1,
                            'od_original_qty':1,
                            'od_original_price':bi_ext_exp,
                            'od_original_unit_cost':bi_ext_exp_cost,
                            'purchase_price':bi_ext_exp_cost,
                            'price_unit':bi_ext_exp,
                            'od_cost_sheet_id':self.id,
                            'od_tab_type':'imp',
                            'tax_id':tsvat,
#                             'tax_id':[[6,False,[line.tax_id.id]]],
                            'od_analytic_acc_id':project_bim,
                            'od_sup_unit_cost':0,
                                }))
            for bim_line in self.manpower_manual_line:
                bim_price +=  bim_line.qty * bim_line.unit_price
                bim_cost += bim_line.qty * bim_line.unit_cost
            if self.bim_imp_select:
                for bim_line in self.bim_implementation_code_line:
                    bim_price +=  bim_line.qty * bim_line.unit_price
                    bim_cost += bim_line.qty * bim_line.unit_cost
            bim_product_id = self.get_product_id_from_param('product_bim')
            b_lines.append((0,0,{'name':self.get_product_name(bim_product_id),
                                 'product_id':bim_product_id,
                                 'od_manufacture_id':self.get_product_brand(bim_product_id),
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':bim_price,
                                'od_original_unit_cost':bim_cost,
                                'purchase_price':bim_cost,
                                'price_unit':bim_price,
                                'od_cost_sheet_id':self.id,
                                'od_tab_type':'imp',
                                 'tax_id':tsvat,
#                             'tax_id':[[6,False,[line.tax_id.id]]],
                                'od_analytic_acc_id':project_bim,
                                'od_sup_unit_cost':0,
            }))
            if not b_lines:
                raise Warning('NO lines to Create Quotation IMP Tab')
#             Bmn Sale order Generation #Now Amc
        bm_lines = []
        bmn_price = 0.0
        bmn_cost = 0.0
        bmn_exp = 0.0
        bmn_exp_cost = 0.0
        omn_price = 0.0
        omn_cost = 0.0
        omn_exp = 0.0
        omn_exp_cost = 0.0
        if self.included_bmn_in_quotation:
            if not project_bmn:
                raise Warning("Analytic Account Not Selected In AMC Tab, Which is Enabled Included In Quotation,Please Select It")
            for omn_line in self.omn_out_preventive_maintenance_line:
                omn_price += omn_line.qty * omn_line.unit_price
                omn_cost += omn_line.qty * omn_line.unit_cost
            for omn_line in self.omn_out_remedial_maintenance_line:
                omn_price += omn_line.qty * omn_line.unit_price
                omn_cost += omn_line.qty * omn_line.unit_cost
            omn_product_id = self.get_product_id_from_param('product_omn')
            bm_lines.append((0,0,{'name':self.get_product_name(omn_product_id),
                                 'product_id':omn_product_id,
                                 'od_manufacture_id':self.get_product_brand(omn_product_id),
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':omn_price,
                                'od_original_unit_cost':omn_cost,
                                'purchase_price':omn_cost,
                                'price_unit':omn_price,
                                'od_cost_sheet_id':self.id,
                                'od_tab_type':'amc',
                                'tax_id':tsvat,
                                'od_analytic_acc_id':project_bmn,
                                'od_sup_unit_cost':0,
                                }))
            for line in self.omn_spare_parts_line:
                bm_lines.append((0,0,{
                                            'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                             'product_id':line.part_no.id,
                                             'name':line.part_no.description_sale or line.part_no.name,
                                             'product_uom_qty':line.qty,
                                             'od_original_qty':line.qty,
                                             'od_original_price':line.unit_price,
                                             'od_original_unit_cost':line.unit_cost_local,
                                             'purchase_price':line.unit_cost_local,
                                             'price_unit':line.unit_price,
                                              'od_cost_sheet_id':self.id,
                                             'od_tab_type':'amc',
                                             'tax_id':[[6,False,[line.tax_id.id]]],
                                             'od_analytic_acc_id':project_bmn,
                                             'od_sup_unit_cost':0,

                                             }))
            for line in self.omn_maintenance_extra_expense_line:
                omn_exp += line.qty * line.unit_price
                omn_exp_cost += line.qty * line.unit_cost
            omn_exp_product_id = self.get_product_id_from_param('product_omn_extra_expense')
            bm_lines.append((0,0,{'name':self.get_product_name(omn_exp_product_id),
                                'product_id':omn_exp_product_id,
                                'od_manufacture_id':self.get_product_brand(omn_exp_product_id),
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':omn_exp,
                                'od_original_unit_cost':omn_exp_cost,
                                'purchase_price':omn_exp_cost,
                                'price_unit':omn_exp,
                                'od_cost_sheet_id':self.id,
                                'od_tab_type':'amc',
                                 'tax_id':tsvat,
#                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                'od_analytic_acc_id':project_bmn,
                                'od_sup_unit_cost':0,
                                }))

            for bmn_line in self.bmn_it_preventive_line:
                bmn_price += bmn_line.qty * bmn_line.unit_price
                bmn_cost += bmn_line.qty * bmn_line.unit_cost
            for bmn_line in self.bmn_it_remedial_line:
                bmn_price += bmn_line.qty * bmn_line.unit_price
                bmn_cost += bmn_line.qty * bmn_line.unit_cost
            bmn_product_id = self.get_product_id_from_param('product_bmn')
            bm_lines.append((0,0,{'name':self.get_product_name(bmn_product_id),
                                'product_id':bmn_product_id,
                                'od_manufacture_id':self.get_product_brand(bmn_product_id),
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':bmn_price,
                                'od_original_unit_cost':bmn_cost,
                                'purchase_price':bmn_cost,
                                'price_unit':bmn_price,
                                'od_cost_sheet_id':self.id,
                                'od_tab_type':'amc',
                                 'tax_id':tsvat,
#                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                'od_analytic_acc_id':project_bmn,
                                'od_sup_unit_cost':0,
                                }))
            for line in self.bmn_spareparts_beta_it_maintenance_line:
                bm_lines.append((0,0,{
                                            'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                             'product_id':line.part_no.id,
                                              'name':line.part_no.description_sale or line.part_no.name,
                                              'od_original_qty':line.qty,
                                              'od_original_price':line.unit_price,
                                              'od_original_unit_cost':line.unit_cost_local,
                                              'purchase_price':line.unit_cost_local,
                                              'product_uom_qty':line.qty,
                                              'price_unit':line.unit_price,
                                              'od_cost_sheet_id':self.id,
                                              'od_tab_type':'amc',
                                              'tax_id':[[6,False,[line.tax_id.id]]],
                                              'od_analytic_acc_id':project_bmn,
                                              'od_sup_unit_cost':0,
                                             }))
            for line in self.bmn_beta_it_maintenance_extra_expense_line:
                bmn_exp += line.qty * line.unit_price
                bmn_exp_cost += line.qty * line.unit_cost
            bmn_exp_product_id = self.get_product_id_from_param('product_bmn_extra_expense')
            bm_lines.append((0,0,{'name':self.get_product_name(bmn_exp_product_id),
                                'product_id':bmn_exp_product_id,
                                'od_manufacture_id':self.get_product_brand(bmn_exp_product_id),
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':bmn_exp,
                                'od_original_unit_cost':bmn_exp_cost,
                                'purchase_price':bmn_exp_cost,
                                'price_unit':bmn_exp,
                                'od_cost_sheet_id':self.id,
                                'od_tab_type':'amc',
                                'tax_id':tsvat,
#                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                'od_analytic_acc_id':project_bmn,
                                'od_sup_unit_cost':0,
                                }))
            if not bm_lines:
                raise Warning('NO lines to Create Quotation MNT Tab')



#             O&m Sale Generation
        om_r_lines = []
        om_price = 0.0
        om_cost = 0.0
        om_exp = 0.0
        om_exp_cost = 0.0
        if self.included_om_in_quotation:
            if not project_o_m:
                raise Warning("Analytic Account Not Selected In O&amp;M Tab, Which is Enabled Included In Quotation,Please Select It")
            for om_res_line in self.om_residenteng_line:
                om_price +=  om_res_line.qty * om_res_line.unit_price
                om_cost +=  om_res_line.qty * om_res_line.unit_cost
                print "om_price>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",om_price
                print "om_cost>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",om_cost
            print "total om_price>>>>>>>>>>>>>>>>>>>"
            o_m_product_id = self.get_product_id_from_param('product_o_m')
            om_r_lines.append((0,0,{'name':self.get_product_name(o_m_product_id),
                                'product_id':o_m_product_id,
                                'od_manufacture_id':self.get_product_brand(o_m_product_id),
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':om_price,
                                'od_original_unit_cost':om_cost,
                                'purchase_price':om_cost,
                                'price_unit':om_price,
                                'od_cost_sheet_id':self.id,
                                'od_tab_type':'o_m',
                                'od_analytic_acc_id':project_o_m,
                                'tax_id':tsvat,
#                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                'od_sup_unit_cost':0,
                                }))
            for line in self.om_eqpmentreq_line:
                om_r_lines.append((0,0,{
                                            'od_manufacture_id':line.manufacture_id and line.manufacture_id.id or False,
                                             'product_id':line.part_no.id,
                                              'name':line.part_no.description_sale or line.part_no.name,
                                              'od_original_qty':line.qty,
                                              'od_original_price':line.unit_price,
                                              'od_original_unit_cost':line.unit_cost_local,
                                              'purchase_price':line.unit_cost_local,
                                              'product_uom_qty':line.qty,
                                              'price_unit':line.unit_price,
                                              'od_cost_sheet_id':self.id,
                                              'od_tab_type':'o_m',
                                              'tax_id':[[6,False,[line.tax_id.id]]],
                                              'od_analytic_acc_id':project_o_m,
                                              'od_sup_unit_cost':0,
                                             }))
            for line in self.om_extra_line:
                om_exp += line.qty * line.unit_price
                om_exp_cost += line.qty * line.unit_cost
            o_m_exp_product_id = self.get_product_id_from_param('product_o_m_extra_expense')
            om_r_lines.append((0,0,{'name':self.get_product_name(o_m_exp_product_id),
                                'product_id':o_m_exp_product_id,
                                'od_manufacture_id':self.get_product_brand(o_m_exp_product_id),
                                'product_uom_qty':1,
                                'od_original_qty':1,
                                'od_original_price':om_exp,
                                'od_original_unit_cost':om_exp_cost,
                                'purchase_price':om_exp_cost,
                                'price_unit':om_exp,
                                'od_cost_sheet_id':self.id,
                                'od_tab_type':'o_m',
                                 'tax_id':tsvat,
#                                 'tax_id':[[6,False,[line.tax_id.id]]],
                                'od_analytic_acc_id':project_o_m,
                                'od_sup_unit_cost':0,
                                }))
            if not om_r_lines:
                raise Warning('NO lines to Create Quotation O&amp;M Tab')
        od_order_type_id = self.od_order_type_id and self.od_order_type_id.id
        print "om line>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        pprint(om_r_lines)
        if not od_order_type_id:
            raise Warning("Please Select Order Type")
        section_id = self.lead_id and self.lead_id.section_id and self.lead_id.section_id.id or False
        discount = self.special_discount
        so_vals = {
            'partner_id':customer_id,
            'bdm_user_id':bdm_user_id,
            'presale_user_id':presale_user_id,
            'od_order_type_id':od_order_type_id,
            'od_cost_sheet_id':self.id,
            'section_id':section_id,
            'od_discount':discount,
            'od_approved_date':self.approved_date,
        }
        if od_order_type_id in (12,26):
            so_vals['order_policy'] = 'picking'
        so_line_map = {'mat':material_lines,'imp':b_lines,'o_m':om_r_lines,'trn':trn_lines,'amc':bm_lines}

        anal_maped_dict = self.map_analytic_acc(anal_dict)
        if not self.sales_order_generated:
            self.create_analytic_map_sale_order(anal_maped_dict,so_vals,so_line_map)
        else:
            print "values>>>>>>>>>>>>>>>> so line map>>>>>>>>>>>>>",so_line_map
            self.write_analytic_map_sale_order(anal_maped_dict,so_vals,so_line_map)
        self.sales_order_generated = True
        self.state = 'done'

    @api.one
    def recreate_sale(self):
        pass
    @api.one
    def unlink(self):
        if self.state != 'draft':
            raise Warning("You Can Only Delete Draft Cost Sheet")
        return super(od_cost_sheet,self).unlink()
    @api.one
    def compute_value(self):
        curr_fluct = []
        shipping_list =[]
        customs_list =[]
        stock_provision_list = []
        conting_provision_list = []
        group_pool =self.env['od.cost.costgroup.material.line']
        for material in self.mat_main_pro_line:
            unit_amount = material.discounted_unit_supplier_currency * material.qty
            for group in material.group:
                ex_rate =group.currency_exchange_factor
                base_factor = unit_amount * ex_rate
                currency_fluct = base_factor * group.currency_fluctation_provision/100
                shipping = base_factor * group.shipping/100
                customs = base_factor * group.customs/100
                stock_provision = base_factor * group.stock_provision/100
                conting_provision = base_factor * group.conting_provision/100
                curr_fluct.append({'group_id':group.id,'currency_fluct':currency_fluct})
                shipping_list.append({'group_id':group.id,'shipping':shipping})
                customs_list.append({'group_id':group.id,'customs':customs})
                stock_provision_list.append({'group_id':group.id,'stock_provision':stock_provision})
                conting_provision_list.append({'group_id':group.id,'conting_provision':conting_provision})

        # computing currency_fluct value
        c = defaultdict(int)
        for d in curr_fluct:
            c[d['group_id']] += d['currency_fluct']
        currency_fluct_dict=[{'group_id': group_id, 'currency_fluct': currency_fluct} for group_id, currency_fluct in c.items()]
        for val in currency_fluct_dict:
            group_id = val.get('group_id',False)
            curr_amnt = val.get('currency_fluct',0.0)
            group_obj = group_pool.browse(group_id)
            group_obj.currency_fluct_value = curr_amnt

        # computing shipping value
        c = defaultdict(int)
        for d in shipping_list:
            c[d['group_id']] += d['shipping']
        shipping_dict=[{'group_id': group_id, 'shipping': shipping} for group_id, shipping in c.items()]
        for val in shipping_dict:
            group_id = val.get('group_id',False)
            shipping_amnt = val.get('shipping',0.0)
            group_obj = group_pool.browse(group_id)
            group_obj.shipping_value = shipping_amnt


        # computing Customs value
        c = defaultdict(int)
        for d in customs_list:
            c[d['group_id']] += d['customs']
        customs_dict=[{'group_id': group_id, 'customs': customs} for group_id, customs in c.items()]
        for val in customs_dict:
            group_id = val.get('group_id',False)
            customs_amnt = val.get('customs',0.0)
            group_obj = group_pool.browse(group_id)
            group_obj.customs_value = customs_amnt

        # computing stock provision value
        c = defaultdict(int)
        for d in stock_provision_list:
            c[d['group_id']] += d['stock_provision']
        stock_dict=[{'group_id': group_id, 'stock_provision': stock_provision} for group_id, stock_provision in c.items()]
        for val in stock_dict:
            group_id = val.get('group_id',False)
            stock_amnt = val.get('stock_provision',0.0)
            group_obj = group_pool.browse(group_id)
            group_obj.stock_provision_value = stock_amnt

        # computing Conting provision value
        c = defaultdict(int)
        for d in conting_provision_list:
            c[d['group_id']] += d['conting_provision']
        cont_dict=[{'group_id': group_id, 'conting_provision': conting_provision} for group_id, conting_provision in c.items()]
        for val in cont_dict:
            group_id = val.get('group_id',False)
            conting_amnt = val.get('conting_provision',0.0)
            group_obj = group_pool.browse(group_id)
            group_obj.conting_provision_value = conting_amnt

    ###completed this func
    @api.one
    def compute_value_optional(self):
        curr_fluct = []
        shipping_list =[]
        customs_list =[]
        stock_provision_list = []
        conting_provision_list = []
        group_pool =self.env['od.cost.costgroup.optional.line.two']
        for material in self.mat_optional_item_line:
            unit_amount = material.discounted_unit_supplier_currency * material.qty
            for group in material.group_id:
                ex_rate =group.currency_exchange_factor
                base_factor = unit_amount * ex_rate
                currency_fluct = base_factor * group.currency_fluctation_provision/100
                shipping = base_factor * group.shipping/100
                customs = base_factor * group.customs/100
                stock_provision = base_factor * group.stock_provision/100
                conting_provision = base_factor * group.conting_provision/100
                curr_fluct.append({'group_id':group.id,'currency_fluct':currency_fluct})
                shipping_list.append({'group_id':group.id,'shipping':shipping})
                customs_list.append({'group_id':group.id,'customs':customs})
                stock_provision_list.append({'group_id':group.id,'stock_provision':stock_provision})
                conting_provision_list.append({'group_id':group.id,'conting_provision':conting_provision})

        # computing currency_fluct value
        c = defaultdict(int)
        for d in curr_fluct:
            c[d['group_id']] += d['currency_fluct']
        currency_fluct_dict=[{'group_id': group_id, 'currency_fluct': currency_fluct} for group_id, currency_fluct in c.items()]
        for val in currency_fluct_dict:
            group_id = val.get('group_id',False)
            curr_amnt = val.get('currency_fluct',0.0)
            group_obj = group_pool.browse(group_id)
            group_obj.currency_fluct_value = curr_amnt

        # computing shipping value
        c = defaultdict(int)
        for d in shipping_list:
            c[d['group_id']] += d['shipping']
        shipping_dict=[{'group_id': group_id, 'shipping': shipping} for group_id, shipping in c.items()]
        for val in shipping_dict:
            group_id = val.get('group_id',False)
            shipping_amnt = val.get('shipping',0.0)
            group_obj = group_pool.browse(group_id)
            group_obj.shipping_value = shipping_amnt


        # computing Customs value
        c = defaultdict(int)
        for d in customs_list:
            c[d['group_id']] += d['customs']
        customs_dict=[{'group_id': group_id, 'customs': customs} for group_id, customs in c.items()]
        for val in customs_dict:
            group_id = val.get('group_id',False)
            customs_amnt = val.get('customs',0.0)
            group_obj = group_pool.browse(group_id)
            group_obj.customs_value = customs_amnt

        # computing stock provision value
        c = defaultdict(int)
        for d in stock_provision_list:
            c[d['group_id']] += d['stock_provision']
        stock_dict=[{'group_id': group_id, 'stock_provision': stock_provision} for group_id, stock_provision in c.items()]
        for val in stock_dict:
            group_id = val.get('group_id',False)
            stock_amnt = val.get('stock_provision',0.0)
            group_obj = group_pool.browse(group_id)
            group_obj.stock_provision_value = stock_amnt

        # computing Conting provision value
        c = defaultdict(int)
        for d in conting_provision_list:
            c[d['group_id']] += d['conting_provision']
        cont_dict=[{'group_id': group_id, 'conting_provision': conting_provision} for group_id, conting_provision in c.items()]
        for val in cont_dict:
            group_id = val.get('group_id',False)
            conting_amnt = val.get('conting_provision',0.0)
            group_obj = group_pool.browse(group_id)
            group_obj.conting_provision_value = conting_amnt
    # completed

class od_date_log_history(models.Model):
    _name = 'od.date.log.history'
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    name = fields.Char(string='Name')
    date = fields.Datetime(string="Date")
class od_customer_reg(models.Model):
    _name ='od.customer.reg'
    name = fields.Char('Customer Registration')

class od_doc_type(models.Model):
    _name ='od.doc.type'
    name = fields.Char(string='Name')

class od_deadline_type(models.Model):
    _name ='od.deadline.type'
    name = fields.Char(string='Name')

class od_reviewer_comment(models.Model):
    _name = 'od.reviewer.comment'
    name = fields.Char('Comment')

class od_support_doc_line(models.Model):
    _name ='od.support.doc.line'
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet')
    doc_type_id = fields.Many2one('od.doc.type',string='Document Type')
    date = fields.Date(string='Date')
    ref = fields.Char(string='Reference')
    rev_comment_id = fields.Many2one('od.reviewer.comment',string="Reviewer Comment")
    fin_comment_id  = fields.Many2one('od.finance.comment','Finance Comment')
class od_deadlines(models.Model):
    _name = 'od.deadlines'
    _inherit = 'od.support.doc.line'
    deadline_type_id = fields.Many2one('od.deadline.type',string='Deadline Type')
    DOM = [
        ('mat','Material Delivery Deadline'),
        ('project_start','Project Start Deadline'),
        ('project_close','Project Closing Deadline'),
        ('maint_start','Maintenance Start Deadline'),
        ('maint_close','Maintenance Closing Deadline'),
        ('availability','Availability of Resident Engineers Deadline'),
        ('start','Start of Operations Deadline'),
        ('end','End of Operations Deadline'),

    ]
    deadline_type = fields.Selection(DOM,string="Deadline Type")
    fin_comment_id  = fields.Many2one('od.finance.comment','Finance Comment')
class od_payment_type(models.Model):
    _name='od.payment.type'
    name = fields.Char('Payment Type')
class od_payment_schedule(models.Model):
    _name = 'od.payment.schedule'
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    payment_type_id = fields.Many2one('od.payment.type','Payment Type')
    value = fields.Float('Value')
    milestone = fields.Char('Link to Milestone/Workpackage')
    fin_comment_id  = fields.Many2one('od.finance.comment','Finance Comment')

class od_cost_summary_line(models.Model):
    _name = 'od.cost.summary.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    item = fields.Char(string='Item')
    description = fields.Char(string='Description')
    arabic_description = fields.Char(string='Description')
    total_price = fields.Float(string='Total Price')


class od_cost_summary_manufacture_line(models.Model):
    _name = 'od.cost.summary.manufacture.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    manufacture_id = fields.Many2one('od.product.brand',string='Manufacture',required="1")
    cost = fields.Float(string='Cost')
    weight = fields.Float(string='Weight(%)')
    profit = fields.Float(string='Profit')
    profit_percentage = fields.Float(string='Profit(%)')

class od_customer_role(models.Model):
    _name ='od.customer.role'
    name = fields.Char('Customer Role')
class od_customer_closing_cond(models.Model):
    _name ='od.customer.closing.cond'
    name = fields.Char('Customer Closing Condition')
class od_beta_closing_cond(models.Model):
    _name ='od.beta.closing.cond'
    name = fields.Char('Beta Closing Condition')
class od_finance_comment(models.Model):
    _name ='od.finance.comment'
    name = fields.Char('Finance Comment')
# class od_customer_closing_line(models.Model):
#     _name = 'od.customer.closing.line'
#     cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
#     customer_close_cond_id  = fields.Many2one('od.customer.closing.cond','Customer Closing Condition')
#     fin_comment_id  = fields.Many2one('od.finance.comment','Finance Comment')
# class od_beta_closing_line(models.Model):
#     _name ='od.beta.closing.line'
#     _inherit = 'od.customer.closing.line'
#     beta_close_cond_id =fields.Many2one('od.beta.closing.cond','Beta Closing Condition')

class od_comm_matrix(models.Model):
    _name = 'od.comm.matrix'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    partner_id = fields.Many2one('res.partner',string='Customer',domain=[('is_company','=',False)])
    customer_role_id = fields.Many2one('od.customer.role',string='Customer Role')
    rev_comment_id = fields.Many2one('od.reviewer.comment',string="Reviewer Comment")
    fin_comment_id  = fields.Many2one('od.finance.comment','Finance Comment')

class od_cost_summary_extra_line(models.Model):
    _name = 'od.cost.summary.extra.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    material = fields.Char(string='Material',required="1")
    total_sales = fields.Float(string='Total Sales')
    total_cost = fields.Float(string='Total cost')
    profit = fields.Float(string='Profit')
    profit_percentage = fields.Float(string='Profit(%)')
    weight = fields.Float(string='Weight(%)')
    full_outsource = fields.Boolean(string='Full Outsource',default=False)
    do_not_use_equations = fields.Boolean(string='Do Not Use Equations',default=False)

class od_cost_summary_version_line(models.Model):
    _name = 'od.cost.summary.version.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    version = fields.Char(string='Version',required="1")
    date = fields.Date(string='Date')


class od_cost_terms_payment_terms_line(models.Model):
    _name = 'od.cost.terms.payment.terms.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    number = fields.Char(string='Number')
    payment_name = fields.Char(string='Payment Name',required="1")
    payment_percentage = fields.Char(string='Payment(%)')


class od_cost_terms_credit_terms_line(models.Model):
    _name = 'od.cost.terms.credit.terms.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    number = fields.Char(string='Number')
    credit_period = fields.Char(string='Credit Period',required="1")
    max_credit_amount = fields.Float(string='Maximum Credit Amount')
    minimum_credit_amount = fields.Float(string='Minimum Credit Amount')

class od_cost_section_line(models.Model):
    _name = 'od.cost.section.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    section = fields.Char(string='Section')
    name = fields.Char(string='Description')
    _rec_name = 'section'
    @api.multi
    def link_section(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'section.mat.add.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def unlink_section(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        section_id = self.id
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        ctx['section_id'] = section_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'section.mat.remove.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }


class od_cost_opt_section_line(models.Model):
    _name = "od.cost.opt.section.line"
    _inherit = 'od.cost.section.line'
    @api.multi
    def link_section(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'section.opt.add.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def unlink_section(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        opt_section_id = self.id
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        ctx['opt_section_id'] = opt_section_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'section.opt.remove.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }


class od_cost_trn_section_line(models.Model):
    _name = "od.cost.trn.section.line"
    _inherit = 'od.cost.section.line'
    @api.multi
    def link_section(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'section.trn.add.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def unlink_section(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        trn_section_id = self.id
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        ctx['trn_section_id'] = trn_section_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'section.trn.remove.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

class od_proof_cost(models.Model):
    _name = 'od.proof.cost'
    name = fields.Char('Proof Of Cost')


class od_cost_costgroup_material_line(models.Model):
    _name = 'od.cost.costgroup.material.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)


    @api.multi
    def link_costgroup(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'costgroup.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def unlink_costgroup(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        costgroup_id = self.id
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        ctx['group_id'] = costgroup_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'costgroup.remove.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for inst in self.browse(cr, uid, ids, context=context):
            name = inst.name or '/'
            cost_sheet_number = inst.cost_sheet_id.number
            if name and cost_sheet_number:
                name='['+ cost_sheet_number +']' + name
            res.append((inst.id, name))
        return res

    def od_get_currency(self):
        return self.env.user.company_id.currency_id.id
    
    def get_vat(self):
        return self.env.user.company_id.od_tax_id 
    
    def od_supplier_currency(self):
        currency2 = self.env.user.company_id and self.env.user.company_id.od_supplier_currency_id
        if not currency2:
            raise Warning("Please Configure CostGroup Default Supplier Currency")
        return currency2

    def od_get_company_id(self):
        return self.env.user.company_id

    def get_saudi_company_id(self):
        parameter_obj = self.env['ir.config_parameter']
        key =[('key', '=', 'od_beta_saudi_co')]
        company_param = parameter_obj.search(key)
        if not company_param:
            raise Warning(_('Settings Warning!'),_('No Company Parameter Not defined\nconfig it in System Parameters with od_beta_saudi_co!'))
        saudi_company_id = company_param.od_model_id and company_param.od_model_id.id or False
        return saudi_company_id


    def is_saudi_comp(self):
        res = False
        saudi_comp_id = self.get_saudi_company_id()
        user_comp_id = self.env.user.company_id.id
        if user_comp_id == saudi_comp_id:
            res = True
        return res

    def my_value(self,uae_val,saudi_val):
        res = uae_val
        if self.is_saudi_comp():
            res =saudi_val
        return res

    def get_shipping_value(self):
        res = self.my_value(5, 2)
        return res

    def get_custom(self):
        res = self.my_value(1, 5)
        return res

    def get_stock_provision(self):
        res = self.my_value(0.50,1)
        return res
    @api.one
    @api.depends('tax_id')
    def _compute_vat_group(self):
        vat = self.tax_id and self.tax_id.amount or 0.0
        vat = vat * 100
        self.vat = vat

    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id,readonly=True)
    supplier_id = fields.Many2one('res.partner',domain=[('supplier','=',True)],string="Manufacturer")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    round_up = fields.Selection([(1,'0'),(2,'1'),(3,'2'),(4,'No Round')],string="Round Up",default=4)
    cost_group_number = fields.Char(string='Number')
    name = fields.Char(string='Description',required="1")
    sales_currency_id = fields.Many2one('res.currency',string='Sales Currency',default=od_get_currency)
    customer_discount = fields.Float(string='Customer Discount(%)')
    profit = fields.Float(string='Profit(%)')
    supplier_discount = fields.Float(string='Supplier Discount(%)')
    supplier_currency_id = fields.Many2one('res.currency',string='Supplier Currency',default=od_supplier_currency)
    currency_exchange_factor = fields.Float(string='Currency Exchange Factor',digits=(6, 4))
    currency_fluctation_provision = fields.Float(string='Currency Fluctuation Provision')
    currency_fluct_value = fields.Float(string='Currency Fluct.Value',readonly=True)
    shipping = fields.Float(string='Shipping(%)',default=get_shipping_value)
    shipping_value = fields.Float(string="Shipping Value",readonly=True)
    customs = fields.Float(string='Customs(%)',default=get_custom)
    customs_value = fields.Float(string='Customs Value',readonly=True)
    stock_provision = fields.Float(string='Stock Provision',default=get_stock_provision)
    stock_provision_value = fields.Float(string='Stock Provision Value',readonly=True)
    conting_provision = fields.Float(string='Conting Provision',default=0.50)
    conting_provision_value = fields.Float(string='Conting Provision Value',readonly=True)
    proof_of_cost  = fields.Many2one('od.proof.cost','Proof Of Cost')
    tax_id = fields.Many2one('account.tax',string="Tax",default=get_vat)
    vat = fields.Float(string="Vat %",compute='_compute_vat_group')
    
    
        
    
#     @api.onchange('supplier_currency_id')
#     def onchange_supp_currency(self):
#         if self.supplier_currency_id:
#             rate = self.supplier_currency_id.rate_silent
#             self.currency_exchange_factor =1/rate

    @api.onchange('sales_currency_id','supplier_currency_id')
    def onchange_currency_rate(self):
        if self.sales_currency_id and self.supplier_currency_id:
            curr = self.env['res.currency']

            from_currency, to_currency = self.sales_currency_id,self.supplier_currency_id
            rate = curr._get_conversion_rate(from_currency, to_currency)

            exchange_fact = 1/rate
            print "exchange factor>>>>>>>>>>>>>>>>>>>>>>",exchange_fact
            exchange_fact= float_round(exchange_fact, precision_rounding=to_currency.rounding)
            print "exchange factor>>>>>>>>>>>>>>>>>>>>>>",exchange_fact,"##",to_currency.rounding
            self.currency_exchange_factor =exchange_fact
    @api.onchange('supplier_id')
    def onchange_partner_id(self):
        if self.supplier_id:
            part = self.supplier_id
            currency_id = part.property_product_pricelist_purchase and part.property_product_pricelist_purchase.currency_id and part.property_product_pricelist_purchase.currency_id.id
            self.supplier_currency_id = currency_id




class od_cost_costgroup_optional_line_two(models.Model):

    _name = 'od.cost.costgroup.optional.line.two'
    _inherit = 'od.cost.costgroup.material.line'
    @api.multi
    def link_costgroup(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'costgroup.opt.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def unlink_costgroup(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        costgroup_id = self.id
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        ctx['group_id'] = costgroup_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'costgroup.opt.remove.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }



class od_cost_costgroup_extra_expenase_line(models.Model):

    _name = 'od.cost.costgroup.extra.expense.line'
    _inherit = 'od.cost.costgroup.material.line'
    @api.multi
    def link_costgroup(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'costgroup.extra.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    @api.multi
    def unlink_costgroup(self):
        context = self.env.context
        cost_sheet_id = self.cost_sheet_id and self.cost_sheet_id.id or False
        costgroup_id = self.id
        ctx =  context.copy()
        ctx['cost_sheet_id'] = cost_sheet_id
        ctx['group_id'] = costgroup_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'costgroup.extra.remove.wiz',
            'context':ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }



class od_cost_costgroup_it_service_line(models.Model):
    _name = 'od.cost.costgroup.it.service.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for inst in self.browse(cr, uid, ids, context=context):
            name = inst.name or '/'
            cost_sheet_number = inst.cost_sheet_id.number
            if name and cost_sheet_number:
                name='[' +  cost_sheet_number  + ']' + name
            res.append((inst.id, name))
        return res

    def od_get_company_id(self):
        return self.env.user.company_id
    
    
    def get_vat(self):
        return self.env.user.company_id.od_tax_id and self.env.user.company_id.od_tax_id.id or False
    @api.one
    @api.depends('tax_id')
    def _compute_vat_group(self):
        vat = self.tax_id and self.tax_id.amount or 0.0
        vat = vat * 100
        self.vat = vat
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id,readonly=True)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    cost_group_number = fields.Char(string='Number')
    name = fields.Char(string='Description',required="1")
    sales_currency_id = fields.Many2one('res.currency',string='Sales Currency')
    customer_discount = fields.Float(string='Customer Discount(%)')
    profit = fields.Float(string='Profit(%)')
    proof_of_cost  = fields.Many2one('od.proof.cost','Proof Of Cost')
    vat = fields.Float(string="Vat %",compute="_compute_vat_group")
    tax_id = fields.Many2one('account.tax',string="Tax",default=get_vat)


class od_cost_mat_main_pro_line(models.Model):
    _name = 'od.cost.mat.main.pro.line'
    _order = 'item_int ASC'


    @api.one
    @api.depends('qty','unit_cost_local','group')
    def _compute_unit_price(self):
        self.line_cost_local_currency = self.qty * self.unit_cost_local
       
        if self.group:
            group_obj = self.group
            profit = group_obj.profit/100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%group_obj.name)
            round_up_val = group_obj.round_up or 3
            round_up_val -=1
            customer_discount = group_obj.customer_discount/100
            unit_cost_local = self.unit_cost_local
#             unit_price = (unit_cost_local / (1-profit)) - (unit_cost_local * customer_discount)
            unit = unit_cost_local/(1-profit)
            unit_price = unit *(1-customer_discount)
            if round_up_val < 3:
                unit_price = round(unit_price,round_up_val)
            self.unit_price = unit_price
         

    @api.one
    @api.depends('unit_cost_supplier_currency','supplier_discount')
    def _compute_supplier_discount(self):
        if self.unit_cost_supplier_currency:
            unit_cost_supplier_currency = self.unit_cost_supplier_currency
            supplier_discount = self.supplier_discount/100
            discount_value = unit_cost_supplier_currency * supplier_discount
            discounted_unit_price = unit_cost_supplier_currency - discount_value
            group_obj = self.group
            ex_rate = group_obj.currency_exchange_factor
            min_qty =self.min_order
            sale_qty = self.qty
            if min_qty <= sale_qty:
                base_factor = discounted_unit_price * ex_rate
            else:
                if sale_qty:
                    base_factor = ((discounted_unit_price*min_qty)/sale_qty)* ex_rate
                else:
                    base_factor = 0
            currency_fluct = group_obj.currency_fluctation_provision/100
            shipping = group_obj.shipping/100
            customs = group_obj.customs/100
            stock_provision = group_obj.stock_provision/100
            conting_provision = group_obj.conting_provision/100
            unit_cost_local = base_factor + base_factor * currency_fluct + base_factor * shipping + base_factor * customs + base_factor * stock_provision + base_factor * conting_provision
            round_up_val = group_obj.round_up or 3
            round_up_val -=1
            if round_up_val <3:
                unit_cost_local = round(unit_cost_local,round_up_val)


            self.unit_cost_local = unit_cost_local
            self.discounted_unit_supplier_currency = discounted_unit_price


    @api.one
    @api.depends('discounted_unit_supplier_currency','qty','min_order')
    def _discounted_total_unit(self):
        qty = self.qty
        min_order = self.min_order
        if qty > min_order:
            self.discounted_total_supplier_currency = self.discounted_unit_supplier_currency * qty
        else:
            self.discounted_total_supplier_currency = self.discounted_unit_supplier_currency * min_order
    @api.one
    @api.depends('group')
    def _compute_currency_supp_discount(self):
        if self.group:
            group_obj = self.group
            self.supplier_currency_id = group_obj.supplier_currency_id and group_obj.supplier_currency_id.id
            sales_currency_id = group_obj.sales_currency_id and group_obj.sales_currency_id.id
            supplier_discount = group_obj.supplier_discount
            self.sales_currency_id = sales_currency_id
            self.supplier_discount = supplier_discount
#             if not self.tax_id:
#                 self.tax_id = group_obj.tax_id and group_obj.tax_id.id

    @api.one
    @api.depends('qty','unit_price','new_unit_price')
    def _compute_line_price(self):
        fixed = self.fixed
        if not fixed:
            self.line_price = self.qty * self.unit_price
        else:
            self.line_price = self.qty * self.new_unit_price
    @api.one
    @api.depends('line_price','line_cost_local_currency')
    def _compute_profit(self):
        self.profit = round(self.line_price )- round(self.line_cost_local_currency)
    @api.one
    @api.depends('line_price','profit')
    def _compute_profit_percentage(self):
        if self.line_price:
            self.profit_percentage = (self.profit/self.line_price)*100

    
    
    @api.one 
    @api.depends('tax_id','line_price','qty')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value = self.line_price * vat
            self.vat_value = vat_value
            
            
#     
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value


    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    check = fields.Boolean(string="Check")
    item = fields.Char(string='Item')
    item_int = fields.Integer(string="Item Number")
    manufacture_id = fields.Many2one('od.product.brand',string='Manufacturer',required=True)
    part_no = fields.Many2one('product.product',string='Part No',required=True)
    name = fields.Text(string='_________Description_______',required="1")
    types = fields.Many2one('od.product.type',string='Type',required=True)
    uom_id = fields.Many2one('product.uom',string='UOM',required=True)
    qty = fields.Integer(string='Qty',default=1)
    unit_price = fields.Float(string="Unit Sale",compute="_compute_unit_price")
    temp_unit_price = fields.Float(string="Temp Unit Price")
    new_unit_price = fields.Float(string="Fixed Unit Sale")
    fixed = fields.Boolean(string="Price Fix")
    
    line_price = fields.Float(string='Total Sale', compute='_compute_line_price')
    group = fields.Many2one('od.cost.costgroup.material.line',string='Group',copy=True)
    section_id = fields.Many2one('od.cost.section.line',string='Section',copy=True)
    sales_currency_id = fields.Many2one('res.currency',string='Sales Currency',compute='_compute_currency_supp_discount')
    unit_cost_local = fields.Float(string='Unit Cost Local', compute='_compute_supplier_discount')
    line_cost_local_currency = fields.Float(string='Line Cost Local Currency',compute="_compute_unit_price")
    profit = fields.Float(string='Profit', compute='_compute_profit')
    profit_percentage = fields.Float(string='Profit(%)', compute='_compute_profit_percentage')
    supplier_currency_id = fields.Many2one('res.currency',string='Supplier Currency',compute="_compute_currency_supp_discount")
    min_order = fields.Integer(string='Min Order',default=1)
    unit_cost_supplier_currency = fields.Float(string='List Price')
    supplier_discount = fields.Float(string='Supplier Discount',compute='_compute_currency_supp_discount')
    discounted_unit_supplier_currency = fields.Float(string='Discounted Unit Supplier Currency', compute='_compute_supplier_discount')
    discounted_total_supplier_currency = fields.Float(string='Discounted Total Supplier Currency',  compute='_discounted_total_unit')
    show_main_pro_line = fields.Boolean(string='Show to Customer',default=False)
    ren = fields.Boolean(string='REN')
    tax_id = fields.Many2one('account.tax',string="Tax")
    vat = fields.Float(string="VAT %",compute='_compute_vat')
    vat_value = fields.Float(sttring="VAT Value",compute='_compute_vat',)


    @api.onchange('part_no')
    def onchange_product_id(self):
        if self.part_no.id:
            part_no = self.part_no.id
            prod = self.env['product.product'].browse(part_no)
            self.name = prod.description
            if not prod.description:
                self.name = prod.name
            self.types = prod.od_pdt_type_id.id
            self.uom_id = prod.uom_id.id



class od_cost_mat_optional_item_line(models.Model):

    _name = 'od.cost.mat.optional.item.line'
    _order = "item_int ASC"




    


    @api.one
    @api.depends('qty','unit_cost_local','group_id')
    def _compute_unit_price(self):
        self.line_cost_local_currency = self.qty * self.unit_cost_local
        # prev_unit_price = self.temp_unit_price
        if self.group_id:
            group_obj = self.group_id
            profit = group_obj.profit/100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%group_obj.name)
            round_up_val = group_obj.round_up or 3
            round_up_val -=1
            customer_discount = group_obj.customer_discount/100
            unit_cost_local = self.unit_cost_local
#             unit_price = (unit_cost_local / (1-profit)) - (unit_cost_local * customer_discount)
            unit_price = (unit_cost_local / (1-profit)) 
            unit_price = unit_price * (1-customer_discount)
            if round_up_val < 3:
                unit_price = round(unit_price,round_up_val)
            # freeze = self.cost_sheet_id and self.cost_sheet_id.freeze
            print "unit+prizeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",unit_price
            self.unit_price = unit_price
            # if not freeze:
            #     self.unit_price = unit_price
            #     self.temp_unit_price = unit_price
            # else:
            #     self.unit_price = prev_unit_price

    @api.one
    @api.depends('unit_cost_supplier_currency','supplier_discount')
    def _compute_supplier_discount(self):
        if self.unit_cost_supplier_currency:
            unit_cost_supplier_currency = self.unit_cost_supplier_currency
            supplier_discount = self.supplier_discount/100
            discount_value = unit_cost_supplier_currency * supplier_discount
            discounted_unit_price = unit_cost_supplier_currency - discount_value
            group_obj = self.group_id
            ex_rate = group_obj.currency_exchange_factor
            min_qty =self.min_order
            sale_qty = self.qty
            if min_qty <= sale_qty:
                base_factor = discounted_unit_price * ex_rate
            else:
                base_factor = ((discounted_unit_price*min_qty)/sale_qty)* ex_rate
            currency_fluct = group_obj.currency_fluctation_provision/100
            shipping = group_obj.shipping/100
            customs = group_obj.customs/100
            stock_provision = group_obj.stock_provision/100
            conting_provision = group_obj.conting_provision/100
            unit_cost_local = base_factor + base_factor * currency_fluct + base_factor * shipping + base_factor * customs + base_factor * stock_provision + base_factor * conting_provision
            round_up_val = group_obj.round_up or 3
            round_up_val -=1
            if round_up_val < 3:
                unit_cost_local = round(unit_cost_local,round_up_val)

            self.unit_cost_local = unit_cost_local
            self.discounted_unit_supplier_currency = discounted_unit_price


    @api.one
    @api.depends('discounted_unit_supplier_currency','qty','min_order')
    def _discounted_total_unit(self):
        qty = self.qty
        min_order = self.min_order
        if qty > min_order:
            self.discounted_total_supplier_currency = self.discounted_unit_supplier_currency * qty
        else:
            self.discounted_total_supplier_currency = self.discounted_unit_supplier_currency * min_order
    @api.one
    @api.depends('group_id')
    def _compute_currency_supp_discount(self):
        if self.group_id:
            group_obj = self.group_id
            self.supplier_currency_id = group_obj.supplier_currency_id and group_obj.supplier_currency_id.id
            sales_currency_id = group_obj.sales_currency_id and group_obj.sales_currency_id.id
            supplier_discount = group_obj.supplier_discount
            self.sales_currency_id = sales_currency_id
            self.supplier_discount = supplier_discount
            self.vat = group_obj.vat

    @api.one
    @api.depends('qty','unit_price')
    def _compute_line_price(self):
        fixed = self.fixed
        if not fixed:
            self.line_price = self.qty * self.unit_price
        else:
            self.line_price = self.qty * self.new_unit_price

    @api.one
    @api.depends('line_price','line_cost_local_currency')
    def _compute_profit(self):
        self.profit = round(self.line_price )- round(self.line_cost_local_currency)
    @api.one
    @api.depends('line_price','profit')
    def _compute_profit_percentage(self):
        if self.line_price and self.profit:
            self.profit_percentage = (self.profit/(self.line_price or 1))*100

#     @api.one
#     @api.depends('supplier_currency_id')
#     def compute_supp_currency(self):
#         if self.supplier_currency_id:
#             from_currency = self.env.user.company_id.currency_id
#             converted_amount = from_currency.compute(self.unit_cost_supplier_currency, self.supplier_currency_id)
#             self.unit_cost_supplier_currency = converted_amount


    @api.one 
    @api.depends('tax_id','line_price','qty')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value = self.line_price * vat
            self.vat_value = vat_value

    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade')
    item = fields.Char(string='Item')
    item_int = fields.Integer(string="Item Number")
    check = fields.Boolean(string="Check")
    manufacture_id = fields.Many2one('od.product.brand',string='Manufacturer',required=True)
    part_no = fields.Many2one('product.product',string='Part No',required=True)
    name = fields.Char(string='_________Description_______',required="1")
    types = fields.Many2one('od.product.type',string='Type',required=True)
    uom_id = fields.Many2one('product.uom',string='UOM',required=True)
    qty = fields.Integer(string='Qty',default=1)
    unit_price = fields.Float(string="Unit Sale",compute="_compute_unit_price")
    temp_unit_price = fields.Float(string="Temp Unit Price")
    new_unit_price = fields.Float(string="Fixed Unit Sale")
    fixed = fields.Boolean(string="Price Fix")
    
    line_price = fields.Float(string='Total Sale',readonly=True, compute='_compute_line_price')
    group_id = fields.Many2one('od.cost.costgroup.optional.line.two',string='Group',copy=True)
    opt_section_id = fields.Many2one('od.cost.opt.section.line',string='Section',copy=True)
    sales_currency_id = fields.Many2one('res.currency',string='Sales Currency',readonly=True, compute='_compute_currency_supp_discount')
    unit_cost_local = fields.Float(string='Unit Cost Local',readonly=True, compute='_compute_supplier_discount')
    line_cost_local_currency = fields.Float(string='Line Cost Local Currency',compute="_compute_unit_price")
    profit = fields.Float(string='Profit',readonly=True, compute='_compute_profit')
    profit_percentage = fields.Float(string='Profit(%)',readonly=True, compute='_compute_profit_percentage')
    supplier_currency_id = fields.Many2one('res.currency',string='Supplier Currency',readonly=True,compute="_compute_currency_supp_discount")
    min_order = fields.Integer(string='Min Order',default=1)
    unit_cost_supplier_currency = fields.Float(string='List Price')
    supplier_discount = fields.Float(string='Supplier Discount',readonly=True, compute='_compute_currency_supp_discount')
    discounted_unit_supplier_currency = fields.Float(string='Discounted Unit Supplier Currency', readonly=True, compute='_compute_supplier_discount')
    discounted_total_supplier_currency = fields.Float(string='Discounted Total Supplier Currency', readonly=True, compute='_discounted_total_unit')
    show_main_pro_line = fields.Boolean(string='Show to Customer',default=False)
    ren = fields.Boolean(string='REN')
    tax_id = fields.Many2one('account.tax',string="Tax")
    vat = fields.Float(string="VAT %",compute="_compute_vat")
    vat_value = fields.Float(sttring="VAT Value",compute='_compute_vat')
    
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value


  

#     @api.onchange('unit_cost_supplier_currency','supplier_discount')
#     def onchange_supplier_discount(self):
#         if self.unit_cost_supplier_currency:
#             unit_cost_supplier_currency =self.unit_cost_supplier_currency
#             supplier_discount = self.supplier_discount/100
#             discount_value = unit_cost_supplier_currency * supplier_discount
#             discounted_unit_price = unit_cost_supplier_currency - discount_value
#             group_obj = self.group_id
#             ex_rate = group_obj.currency_exchange_factor
#
#             min_qty =self.min_order
#             sale_qty = self.qty
#             if min_qty <= sale_qty:
#                 base_factor = discounted_unit_price * ex_rate
#             else:
#                 base_factor = ((discounted_unit_price*min_qty)/sale_qty)* ex_rate
#             currency_fluct = group_obj.currency_fluctation_provision/100
#             shipping = group_obj.shipping/100
#             customs = group_obj.customs/100
#             stock_provision = group_obj.stock_provision/100
#             conting_provision = group_obj.conting_provision/100
#             unit_cost_local = base_factor + base_factor * currency_fluct + base_factor * shipping + base_factor * customs + base_factor * stock_provision + base_factor * conting_provision
#             self.unit_cost_local = unit_cost_local
#             self.discounted_unit_supplier_currency = discounted_unit_price


#     @api.onchange('min_order','discounted_unit_supplier_currency','qty')
#     def onchange_discounted_single_unit(self):
#         qty = self.qty
#         min_order = self.min_order
#         print "qtyuyyyy",qty,min_order
#         if qty > min_order:
#             self.discounted_total_supplier_currency = self.discounted_unit_supplier_currency * qty
#         else:
#             self.discounted_total_supplier_currency = self.discounted_unit_supplier_currency * min_order
#     @api.onchange('min_order','qty','discounted_unit_supplier_currency')
#     def onchange_min_order(self):
#         if self.min_order:
#             if self.min_order > self.qty:
#                 self.discounted_total_supplier_currency = self.discounted_unit_supplier_currency * self.min_order
#
#
#
#     @api.onchange('group_id')
#     def onchange_cost_group(self):
#         if self.group_id:
#             group_obj = self.group_id
#             self.supplier_currency_id = group_obj.supplier_currency_id and group_obj.supplier_currency_id.id
#             sales_currency_id = group_obj.sales_currency_id and group_obj.sales_currency_id.id
#             supplier_discount = group_obj.supplier_discount
#             self.sales_currency_id = sales_currency_id
#             self.supplier_discount = supplier_discount
#     @api.onchange('supplier_currency_id')
#     def onchange_supp_currency(self):
#         if self.supplier_currency_id:
#             from_currency = self.env.user.company_id.currency_id
#             converted_amount = from_currency.compute(self.unit_cost_supplier_currency, self.supplier_currency_id)
#             self.unit_cost_supplier_currency = converted_amount

    @api.onchange('part_no')
    def onchange_product_id(self):
        if self.part_no.id:
            part_no = self.part_no.id
            prod = self.env['product.product'].browse(part_no)
            self.name = prod.description
            if not prod.description:
                self.name = prod.name
            self.types = prod.od_pdt_type_id.id
            self.uom_id = prod.uom_id.id
#             price = prod.list_price
#             self.unit_cost_supplier_currency = price
#     @api.onchange('qty','unit_price')
#     def onchange_qty(self):
#         self.line_price = self.qty * self.unit_price
#
#     @api.onchange('line_price','line_cost_local_currency')
#     def onchange_prices_to_profit(self):
#         self.profit = self.line_price - self.line_cost_local_currency
#         print "profit>>>>>>>>>>>>>>.oonchange>>>>>>>>>>>>>>>>>>>>>>",self.line_price,self.line_cost_local_currency
#     @api.onchange('line_price','profit')
#     def onchange_profit_per(self):
#         if self.line_price:
#             self.profit_percentage = (self.profit/self.line_price)*100


class od_cost_mat_brand_weight(models.Model):
    _name = 'od.cost.mat.brand.weight'

    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)


    @api.one
    @api.depends('total_sale','total_cost')
    def _compute_vals(self):
        total_sale = round(self.total_sale)
        total_cost = round(self.total_cost)
        profit = total_sale- total_cost
        self.profit = profit
        all_brand_cost = self.all_brand_cost
        if total_sale:
            self.profit_percent =  (profit /(total_sale or 1.0)) * 100
        if all_brand_cost:
            self.weight = (total_cost /(all_brand_cost or 1.0)) * 100


    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    manufacture_id = fields.Many2one('od.product.brand',string='Brand')
    total_sale = fields.Float(string="Total Brand Sales")
    total_cost = fields.Float(string="Total Brand cost")
    all_brand_cost = fields.Float(string="All Brand Cost")
    profit = fields.Float(string="Profit",compute="_compute_vals")
    profit_percent = fields.Float(string="Profit %",compute="_compute_vals")
    weight  = fields.Float(string="Weight",compute="_compute_vals")
    

class od_cost_mat_group_weight(models.Model):
    _name = 'od.cost.mat.group.weight'

    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)


    @api.one
    @api.depends('total_sale','total_cost')
    def _compute_vals(self):
        total_sale = round(self.sale_aftr_disc)
        total_cost = round(self.total_cost)
        profit = total_sale- total_cost
        self.profit = profit
        all_group_cost = self.all_group_cost
        if total_sale:
            self.profit_percent =  (profit /(total_sale or 1.0)) * 100
        if all_group_cost:
            self.weight = (total_cost /(all_group_cost or 1.0)) * 100


    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    pdt_grp_id = fields.Many2one('od.product.group',string='Product Group')
    total_sale = fields.Float(string="Sales Before Disc")
    disc = fields.Float(string="Disc %")
    sale_aftr_disc = fields.Float(string="Sales After Disc")
    total_cost = fields.Float(string="Total Group cost")
    all_group_cost = fields.Float(string="All Group Cost")
    profit = fields.Float(string="Profit",compute="_compute_vals")
    profit_percent = fields.Float(string="Profit %",compute="_compute_vals")
    weight  = fields.Float(string="Weight",compute="_compute_vals")


class od_cost_imp_weight(models.Model):
    _name = 'od.cost.impl.group.weight'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    tab = fields.Selection([('bim','BIM'),('oim','OIM')],string="IMP")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    pdt_grp_id = fields.Many2one('od.product.group',string='Product Group')
    total_sale = fields.Float(string="Sales")
    disc = fields.Float(string="Disc %")
    sale_aftr_disc = fields.Float(string="Sales After Disc")
    total_cost = fields.Float(string="Cost")
    profit = fields.Float(string="Profit")


class od_cost_amc_weight(models.Model):
    _name = 'od.cost.amc.group.weight'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    tab = fields.Selection([('bmn','BMN'),('omn','OMN')],string="AMC")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    pdt_grp_id = fields.Many2one('od.product.group',string='Product Group')
    total_sale = fields.Float(string="Sales")
    disc = fields.Float(string="Disc %")
    sale_aftr_disc = fields.Float(string="Sales After Disc")
    total_cost = fields.Float(string="Cost")
    profit = fields.Float(string="Profit")
    

class od_cost_om_weight(models.Model):
    _name = 'od.cost.om.group.weight'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    tab = fields.Selection([('om','O&M')],string="O&M")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    pdt_grp_id = fields.Many2one('od.product.group',string='Product Group')
    total_sale = fields.Float(string="Sales")
    disc = fields.Float(string="Disc %")
    sale_aftr_disc = fields.Float(string="Sales After Disc")
    total_cost = fields.Float(string="Cost")
    profit = fields.Float(string="Profit")

class od_cost_extra_expense_weight(models.Model):
    _name = 'od.cost.extra.group.weight'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    tab = fields.Selection([('mat','MAT'),('trn','TRN')],string="Extra Expense")
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    pdt_grp_id = fields.Many2one('od.product.group',string='Product Group')
    total_sale = fields.Float(string="Sales")
    disc = fields.Float(string="Disc %")
    sale_aftr_disc = fields.Float(string="Sales After Disc")
    total_cost = fields.Float(string="Cost")
    profit = fields.Float(string="Profit")


class od_cost_summary_weight(models.Model):
    _name = 'od.cost.summary.group.weight'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    pdt_grp_id = fields.Many2one('od.product.group',string='Product Group')
    total_sale = fields.Float(string="Sales")
    disc = fields.Float(string="Disc %")
    sale_aftr_disc = fields.Float(string="Sales After Disc")
    total_cost = fields.Float(string="Cost")
    profit = fields.Float(string="Profit")
    manpower_cost = fields.Float(string="Manpower Cost")
    total_gp = fields.Float(string="Total GP")
    
    
    @api.one
    @api.depends('total_sale','total_cost')
    def _compute_vals(self):
        total_sale = round(self.sale_aftr_disc)
        total_cost = round(self.total_cost)
        profit = total_sale- total_cost
        if total_sale:
            self.profit_percent =  (profit /total_sale) * 100
       
    profit_percent = fields.Float(string="Profit %",compute="_compute_vals")


class od_cost_mat_extra_expense_line(models.Model):
    _name = 'od.cost.mat.extra.expense.line'
    _order = "item_int ASC"
    @api.one
    @api.depends('qty','unit_cost','unit_price','new_unit_price','group')
    def compute_calculation(self):
        if self.group:
            profit = self.group.profit /100
            self.tax_id = self.group and self.group.tax_id and self.group.tax_id.id or False
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%self.group.name)
            discount = self.group.customer_discount/100
            unit_cost = self.unit_cost
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.unit_price = unit_price

        if self.qty or self.unit_cost:
            self.line_cost = self.qty * self.unit_cost
        fixed = self.fixed
        if fixed:
            self.line_price = self.qty * self.new_unit_price 
        else:
            self.line_price = self.qty * self.unit_price

    @api.one
    @api.depends('qty','list_price','unit_price2','new_unit_price','group2')
    def compute_calculation2(self):
        if self.group2:
            self.tax_id = self.group2 and self.group2.tax_id and self.group2.tax_id.id or False
            profit = self.group2.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%self.group.name)
            discount = self.group2.customer_discount/100
            list_price = self.list_price
            supplier_discount = (self.group2.supplier_discount)/100
            discount_value = list_price * supplier_discount
            discounted_unit_cost = list_price - discount_value
            ex_rate = self.group2.currency_exchange_factor
            base_factor = discounted_unit_cost * ex_rate
            currency_fluct = self.group2.currency_fluctation_provision/100
            shipping = self.group2.shipping/100
            customs = self.group2.customs/100
            stock_provision = self.group2.stock_provision/100
            conting_provision = self.group2.conting_provision/100
            unit_cost_local = base_factor + base_factor * currency_fluct + base_factor * shipping + base_factor * customs + base_factor * stock_provision + base_factor * conting_provision
            round_up_val = self.group2.round_up or 3
            round_up_val -=1
            if round_up_val <3:
                unit_cost_local = round(unit_cost_local,round_up_val)
            self.unit_cost_local = unit_cost_local
#             unit_price = (unit_cost_local / (1-profit)) - (unit_cost_local * discount)
            unit_price = (unit_cost_local / (1-profit))
            unit_price = unit_price * (1-discount)
            self.unit_price2 = unit_price
#             self.vat = self.group2.vat
        fixed = self.fixed
        if fixed:
            self.line_price2 = self.qty * self.new_unit_price 
        else:
            self.line_price2 = self.qty * self.unit_price2
        if self.qty and self.unit_cost_local:
            self.line_cost_local = self.qty * self.unit_cost_local
    
    @api.one 
    @api.depends('tax_id','line_price','qty','line_price2')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value1 = self.line_price * vat
            self.vat_value = vat_value1
            
            vat_value2 = self.line_price2 * vat
            self.vat_value2 = vat_value2
    
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    item = fields.Char(string='Item')
    item_int = fields.Integer(string="Item Number")
    check = fields.Boolean(string="Check")
    od_product_id = fields.Many2one('product.product',string='Expense',domain=[('type','=','consu')])
    name = fields.Char(string='Description')
    qty = fields.Float(string='Qty',default=1)
    unit_cost = fields.Float(string='Unit Cost')
    line_cost = fields.Float(string='Line Cost',compute='compute_calculation')
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group',copy=True)
    group2 = fields.Many2one('od.cost.costgroup.extra.expense.line',string='Group',copy=True)
    unit_price = fields.Float(string='Unit Price',compute='compute_calculation')
    
    temp_unit_price = fields.Float(string="Temp Unit Price")
    new_unit_price = fields.Float(string="Fixed Unit Sale")
    fixed = fields.Boolean(string="Price Fix")
    
    line_price = fields.Float(string='Line Price',compute='compute_calculation')
    unit_cost_local = fields.Float(string="Unit Cost Local",compute='compute_calculation2')
    line_cost_local = fields.Float(string="Line Cost Local",compute='compute_calculation2')
    list_price = fields.Float(string="List Price")
    unit_price2 = fields.Float(string='Unit Price',compute='compute_calculation2')
    line_price2 = fields.Float(string='Line Price',compute='compute_calculation2')
    show_to_customer = fields.Boolean(string='Show to Customer')
    tax_id = fields.Many2one('account.tax',string="Tax")
    vat = fields.Float(string="VAT %")
    vat_value = fields.Float(sttring="VAT Value",compute="_compute_vat")
    vat_value2 = fields.Float(sttring="VAT Value",compute="_compute_vat")
#     @api.one 
#     @api.onchange('vat','line_price2')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price2
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value

    @api.onchange('od_product_id')
    def onchange_product(self):
        if self.od_product_id:
            self.name = self.od_product_id.description



#     @api.onchange('qty','unit_cost','unit_price')
#     def onchange_qty(self):
#         if self.qty or self.unit_cost:
#             self.line_cost = self.qty * self.unit_cost
#         if self.qty and self.unit_price:
#             self.line_price = self.qty * self.unit_price
#
#     @api.onchange('group','unit_cost')
#     def onchange_group(self):
#         if self.group:
#             profit = self.group.profit /100
#             discount = self.group.customer_discount/100
#             unit_cost = self.unit_cost
#             unit_price = unit_cost + (unit_cost*profit - unit_cost*discount)
#             self.unit_price = unit_price

class od_cost_ren_main_pro_line(models.Model):

    _name = 'od.cost.ren.main.pro.line'
    _order = "item_int ASC"
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    item = fields.Char(string='Item')
    item_int = fields.Integer(string='Item Number')
    check = fields.Boolean(string="Check")
    manufacture_id = fields.Many2one('od.product.brand',string='Manufacture',required="1")
    renewal_package_no = fields.Many2one('product.product',string='Renewal Package No')
    product_p_n = fields.Many2one('product.product',string='Applicable To')
    serial_no = fields.Text(string='Serial No')
    city_id = fields.Many2one("res.country.state", 'City')
    notes = fields.Char('__________________Notes_______________')
    location = fields.Char(string='Location')
    start_date = fields.Date(string='Start Date')
    expiry_date = fields.Date(string='Expiry Date')
    show_main_line = fields.Boolean(string='Show to Customer',default=False)

class od_cost_ren_optional_item_line(models.Model):

    _name = 'od.cost.ren.optional.item.line'
    _inherit ='od.cost.ren.main.pro.line'
    show_optional_line = fields.Boolean(string='Show to Customer',default=False)

class od_bmn_eqp_cov_line(models.Model):
    _name = 'od.bmn.eqp.cov.line'
    _inherit ='od.cost.ren.main.pro.line'
class od_omn_eqp_cov_line(models.Model):
    _name = 'od.omn.eqp.cov.line'
    _inherit ='od.cost.ren.main.pro.line'
class od_o_m_eqp_cov_line(models.Model):
    _name = 'od.o_m.eqp.cov.line'
    _inherit ='od.cost.ren.main.pro.line'

class od_cost_trn_customer_training_line(models.Model):
    _name = 'od.cost.trn.customer.training.line'
    _inherit = 'od.cost.mat.main.pro.line'
    trn_section_id = fields.Many2one('od.cost.trn.section.line',string='Section',copy=True)
# class od_cost_trn_optional_line(models.Model):
#
#
#     _name="od.cost.trn.optional.line"
#     _inherit = 'od.cost.mat.main.pro.line'
#


class od_cost_trn_customer_training_extra_expense_line(models.Model):
    _name = 'od.cost.trn.customer.training.extra.expense.line'
    _inherit = 'od.cost.mat.extra.expense.line'



class od_cost_bim_beta_implimentation_extra_expense_line(models.Model):
    _name = 'od.cost.bim.beta.implimentation.extra.expense.line'
    _inherit = 'od.cost.mat.extra.expense.line'
    
    
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value
    
    
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        group = self.group
        self.tax_id = group.tax_id and group.tax_id.id



#     cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
#     item = fields.Char(string='Item')
#     od_product_id = fields.Many2one('product.product',string='Product')
#     name = fields.Char(string='Description')
#     qty = fields.Float(string='Qty')
#     unit_cost = fields.Float(string='Unit Cost')
#     line_cost = fields.Float(string='Line Cost')
#     bim_show_to_customer = fields.Boolean(string='Show to Customer',default=False)
#
#     @api.onchange('od_product_id')
#     def onchange_product(self):
#         if self.od_product_id:
#             self.name = self.od_product_id.description
#
#     @api.onchange('qty','unit_cost')
#     def onchange_qty(self):
#         if self.qty or self.unit_cost:
#             self.line_cost = self.qty * self.unit_cost


class od_cost_bim_beta_manpower_manual_line(models.Model):
    _name = 'od.cost.bim.beta.manpower.manual.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)

    @api.one
    @api.depends('qty','unit_cost','unit_price','cost_group_id')
    def compute_calc(self):
        if self.cost_group_id:
            profit = self.cost_group_id.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%self.cost_group_id.name)
            discount = self.cost_group_id.customer_discount/100
            unit_cost = self.unit_cost
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.unit_price = unit_price
        if self.qty or self.unit_cost:
            self.line_cost = self.qty * self.unit_cost
        if self.qty or self.unit_price:
            self.line_price = self.qty * self.unit_price
    
    @api.one 
    @api.depends('tax_id','line_price','qty')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value1 = self.line_price * vat
            self.vat_value = vat_value1
           
    
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    sheet_id = fields.Many2one('od.cost.sheet',string='Sheet')
    item = fields.Char(string='Item')
    name = fields.Char(string='Description')
    qty = fields.Float(string='Qty',default=1)
    unit_price = fields.Float(string='Unit Price',compute='compute_calc')
    line_price = fields.Float(string='Line Price',compute='compute_calc')
    unit_cost = fields.Float(string='Unit Cost')
    line_cost = fields.Float(string='Line Cost',compute='compute_calc')
    cost_group_id = fields.Many2one('od.cost.costgroup.it.service.line',string='Cost Group')
    bim_show_to_customer = fields.Boolean(string='Show to Customer',default=False)
    product_id = fields.Many2one('product.product',string='Expense',domain=[('type','=','service')])
    tax_id = fields.Many2one('account.tax',string="Tax")
    vat = fields.Float(string="VAT %",compute='_compute_vat',)
    vat_value = fields.Float(string="VAT Value",compute='_compute_vat',)
    
    
    
    @api.one 
    @api.onchange('cost_group_id')
    def onchange_group(self):
        group = self.cost_group_id 
        self.tax_id = group.tax_id and group.tax_id.id
    
#     
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value


#
#     @api.onchange('product_id')
#     def onchange_product(self):
#         if self.product_id:
#             self.name = self.product_id.description
#             self.unit_cost = self.product_id.standard_price
#     @api.onchange('qty','unit_cost')
#     def onchange_qty(self):
#         if self.qty or self.unit_cost:
#             self.line_cost = self.qty * self.unit_cost
#
#     @api.onchange('cost_group_id','unit_cost')
#     def onchange_group(self):
#
#         if self.cost_group_id:
#             profit = self.cost_group_id.profit /100
#             discount = self.cost_group_id.customer_discount/100
#             unit_cost = self.unit_cost
#             unit_price = unit_cost + (unit_cost*profit - unit_cost*discount)
#             self.unit_price = unit_price
#
#     @api.onchange('qty','unit_price')
#     def onchange_unitprice(self):
#         if self.qty or self.unit_price:
#             self.line_price = self.qty * self.unit_price


class od_cost_bim_beta_implementation_code(models.Model):
    _name = 'od.cost.bim.beta.implementation.code'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    @api.one
    @api.depends('imp_code','qty','unit_price','unit_cost','code_hours','cost_hour','group')
    def compute_calc(self):
        if self.group and self.imp_code and self.cost_hour:
            profit = self.group.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%self.group.name)
            discount = self.group.customer_discount/100
            unit_cost = self.imp_code.expected_act_duration * self.cost_hour
            print "unit cost>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",unit_cost
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.unit_price = unit_price
        if self.imp_code:
            self.code_hours = self.imp_code.expected_act_duration
        if self.qty and self.code_hours:
            self.total_hours = self.qty * self.code_hours
        if self.code_hours and self.cost_hour:
            self.unit_cost = self.code_hours * self.cost_hour
        if self.unit_cost and self.qty:
            self.line_cost = self.unit_cost * self.qty
        if self.unit_price and self.qty:
            self.line_price = self.unit_price * self.qty
    
    
    @api.one 
    @api.depends('tax_id','line_price','qty')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value1 = self.line_price * vat
            self.vat_value = vat_value1
    
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    item = fields.Char(string='Item')
    imp_code = fields.Many2one('od.implementation',string='Implementation Code')
    qty = fields.Float('Qty',default=1)
    unit_price = fields.Float('Unit Sale',compute='compute_calc')
    line_price = fields.Float('Total Sale',compute='compute_calc')
    unit_cost = fields.Float('Unit Cost',compute='compute_calc')
    line_cost = fields.Float('Total Cost',compute='compute_calc')
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group')
    code_hours = fields.Float('Code Hours',compute='compute_calc')
    total_hours = fields.Float('Total Hours',compute='compute_calc')
    cost_hour = fields.Float('Cost / Hour',default=350)
    tax_id = fields.Many2one('account.tax',string="Tax")
    vat = fields.Float(string="VAT %",compute='_compute_vat')
    vat_value = fields.Float(string="VAT Value",compute='_compute_vat')
    
    
    
    
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        group = self.group
        self.tax_id = group.tax_id and group.tax_id.id    
    
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value

    


#
#     @api.onchange('imp_code')
#     def onchange_imp_code(self):
#         if self.imp_code:
#             self.code_hours = self.imp_code.expected_act_duration
#     @api.onchange('qty','unit_price','unit_cost','code_hours','cost_hour')
#     def onchange_qty(self):
#         self.total_hours = self.qty * self.code_hours
#         self.unit_cost = self.code_hours * self.cost_hour
#         self.line_cost = self.unit_cost * self.qty
#         self.line_price = self.unit_price * self.qty
#     @api.onchange('group','unit_cost')
#     def onchange_group(self):
#         if self.group:
#             profit = self.group.profit /100
#             discount = self.group.customer_discount/100
#             unit_cost = self.unit_cost
#             unit_price = unit_cost + (unit_cost*profit - unit_cost*discount)
#             self.unit_price = unit_price

class od_cost_oim_implimentation_price_line(models.Model):
    _name = 'od.cost.oim.implimentation.price.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)

    @api.one
    @api.depends('qty','unit_price','unit_cost','group')
    def compute_calc(self):
        if self.group:
            profit = self.group.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%self.group.name)
            discount = self.group.customer_discount/100
            unit_cost = self.unit_cost
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.unit_price = unit_price
        if self.unit_price and self.qty:
            self.line_price = self.qty * self.unit_price
        if self.unit_cost and self.qty:
            self.line_cost = self.qty * self.unit_cost
    
    
    @api.one 
    @api.depends('tax_id','line_price','qty')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value1 = self.line_price * vat
            self.vat_value = vat_value1
    
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    item = fields.Char(string='Item')
    partner_id = fields.Many2one('res.partner',string='Partner',domain=[('supplier','=',True),('is_company','=',True)])
    name = fields.Char(string='Description')
    qty = fields.Float(string='Qty',default=1)
    unit_price = fields.Float(string='Unit Sale',compute='compute_calc')
    line_price = fields.Float(string='Total Sale',compute='compute_calc')
    unit_cost = fields.Float(string='Unit Cost')
    line_cost = fields.Float(string='Line Cost',compute='compute_calc')
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group')
    show_oim_price_cust = fields.Boolean(string='Show to Customer',default=False)
    tax_id = fields.Many2one('account.tax',string="Tax")
    vat = fields.Float(string="VAT %",compute='_compute_vat')
    vat_value = fields.Float(string="VAT Value",compute='_compute_vat')
    
    
    
    
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        group = self.group
        self.tax_id = group.tax_id and group.tax_id.id
    
    
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value



#     @api.onchange('od_product_id')
#     def onchange_product_id(self):
#         if self.od_product_id.id:
#             product_obj = self.od_product_id
#             self.name = product_obj.name
#             self.unit_price = product_obj.lst_price
#             self.unit_cost = product_obj.standard_price
#     @api.onchange('qty','unit_price')
#     def onchange_unit_price(self):
#         if self.unit_price:
#             self.line_price = self.qty * self.unit_price
#     @api.onchange('qty','unit_cost')
#     def onchange_unit_cost(self):
#         if self.unit_cost:
#             self.line_cost = self.qty * self.unit_cost
#     @api.onchange('group','unit_cost')
#     def onchange_group(self):
#         if self.group:
#             profit = self.group.profit /100
#             discount = self.group.customer_discount/100
#             unit_cost = self.unit_cost
#             unit_price = unit_cost + (unit_cost*profit - unit_cost*discount)
#             self.unit_price = unit_price
class od_cost_oim_extra_expenses_line(models.Model):
    _name = 'od.cost.oim.extra.expenses.line'
    _inherit = 'od.cost.mat.extra.expense.line'
    
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        group = self.group
        self.vat = group.vat
    
    @api.one 
    @api.onchange('vat','line_price')
    def onchange_vat(self):
        vat = self.vat
        line_price = self.line_price
        vat_value = line_price * (vat/100.0)
        self.vat_value = vat_value
#     cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
#     item = fields.Char(string='Item')
# #     product_id = fields.Many2one('product.product','Prouduct')
#     name = fields.Char(string='Description')
#     qty = fields.Float(string='Qty')
#     unit_cost = fields.Float(string='Unit Cost')
#     line_cost = fields.Float(string='Line Cost')
#     show_to_customer = fields.Boolean(string='Show to Customer',default=False)


#     @api.onchange('product_id')
#     def onchange_product_id(self):
#         if self.product_id.id:
#             product_obj = self.product_id
#             self.name = product_obj.name
#             self.unit_price = product_obj.lst_price
#             self.unit_cost = product_obj.standard_price
#     @api.onchange('qty','unit_cost')
#     def onchange_unit_cost(self):
#         if self.unit_cost:
#             self.line_cost = self.qty * self.unit_cost


class od_cost_om_residenteng_line(models.Model):
    _name = 'od.cost.om.residenteng.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    @api.one
    @api.depends('qty','unit_price','unit_cost','line_price','line_cost','group')
    def compute_calc(self):
        if self.group:
            profit = self.group.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%self.group.name)
            discount = self.group.customer_discount/100
            unit_cost = self.unit_cost
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.unit_price = unit_price
        if self.unit_price and self.qty:
            self.line_price = self.qty * self.unit_price
        if self.unit_cost and self.qty:
            self.line_cost = self.qty * self.unit_cost
        if self.line_price :
            self.profit = self.line_price - self.line_cost
            self.profit_percentage = (self.profit/self.line_price)*100

    @api.one 
    @api.depends('tax_id','line_price','qty')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value1 = self.line_price * vat
            self.vat_value = vat_value1
    
    
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    item = fields.Char(string='Item')
    od_product_id = fields.Many2one('product.product',string='Job Position',domain=[('type','=','service')])
    name = fields.Char(string='Description')
    qty = fields.Float(string='Qty',default=1)
    unit_price = fields.Float(string='Unit Price',compute='compute_calc')
    line_price = fields.Float(string='Line Price',compute='compute_calc')
    unit_cost = fields.Float(string='Unit Cost')
    line_cost = fields.Float(string='Line Cost',compute='compute_calc')
    profit = fields.Float(string='Profit',compute='compute_calc')
    profit_percentage = fields.Float(string='Profit(%)',compute='compute_calc')
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group')
    show_to_customer = fields.Boolean(string='Show to Customer',default=False)
    tax_id = fields.Many2one('account.tax',string="Tax")
    vat = fields.Float(string="VAT %",compute='_compute_vat')
    vat_value = fields.Float(string="VAT Value",compute='_compute_vat')
    
    
    
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        group = self.group
        self.tax_id = group.tax_id and group.tax_id
    
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value
#     @api.onchange('od_product_id')
#     def onchange_product_id(self):
#         if self.od_product_id.id:
#             product_obj = self.od_product_id
#             self.name = product_obj.name
#             self.unit_price = product_obj.lst_price
#             self.unit_cost = product_obj.standard_price
#     @api.onchange('qty','unit_price')
#     def onchange_unit_price(self):
#         if self.unit_price:
#             self.line_price = self.qty * self.unit_price
#     @api.onchange('qty','unit_cost','group')
#     def onchange_unit_cost(self):
#         if self.unit_cost:
#             unit_cost = self.unit_cost
#             self.line_cost = self.qty * self.unit_cost
#             group = self.group
#             profit_per = group.profit/100
#             discount = group.customer_discount/100
#             unit_price = unit_cost + (unit_cost * profit_per - unit_cost* discount)
#             self.unit_price = unit_price
#     @api.onchange('line_price','line_cost')
#     def onchange_prices_to_profit(self):
#         self.profit = self.line_price - self.line_cost
#
#     @api.onchange('line_price','profit')
#     def onchange_profit_per(self):
#         if self.line_price:
#             self.profit_percentage = (self.profit/self.line_price)*100




class od_cost_om_eqpmentreq_line(models.Model):
    _name = 'od.cost.om.eqpmentreq.line'
    _inherit = 'od.cost.mat.main.pro.line'


class od_cost_om_extra_line(models.Model):
    _name = 'od.cost.om.extra.line'
    _inherit = 'od.cost.mat.extra.expense.line'

#     cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
#     item = fields.Char(string='Item')
#     name = fields.Char(string='Description')
#     qty = fields.Float(string='Qty')
#     unit_cost = fields.Float(string='Unit Cost')
#     line_cost = fields.Float(string='Line Cost')
#     show_to_customer = fields.Boolean(string='Show to Customer')



class od_cost_omn_out_preventive_maintenance_line(models.Model):
    _name = 'od.cost.omn.out.preventive.maintenance.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    @api.one
    @api.depends('qty','unit_price','unit_cost','line_price','line_cost','group')
    def compute_calc(self):
        if self.group:
            profit = self.group.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%self.group.name)
            discount = self.group.customer_discount/100
            unit_cost = self.unit_cost
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.unit_price = unit_price
        if self.unit_price and self.qty:
            self.line_price = self.qty * self.unit_price
        if self.unit_cost and self.qty:
            self.line_cost = self.qty * self.unit_cost
        if self.line_price :
            self.profit = self.line_price - self.line_cost
            self.profit_percentage = (self.profit/self.line_price)*100

    @api.one 
    @api.depends('tax_id','line_price','qty')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value1 = self.line_price * vat
            self.vat_value = vat_value1

    
    
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    sheet_id = fields.Many2one('od.cost.sheet',string="Sheet")
    item = fields.Char(string='Item')
    od_product_id = fields.Many2one('product.product',string='Product')
    name = fields.Char(string='Description')
    qty = fields.Float(string='Qty',default=1)
    unit_price = fields.Float(string='Unit Price',compute='compute_calc')
    line_price = fields.Float(string='Line Price',compute='compute_calc')
    unit_cost = fields.Float(string='Unit Cost')
    line_cost = fields.Float(string='Line Cost',compute='compute_calc')
    profit = fields.Float(string='Profit',compute='compute_calc')
    profit_percentage = fields.Float(string='Profit(%)',compute='compute_calc')
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group')
    show_to_customer = fields.Boolean(string='Show to Customer')
    tax_id = fields.Many2one('account.tax',string="Tax")
    vat = fields.Float(string="VAT %",compute='_compute_vat')
    vat_value = fields.Float(string="VAT Value",compute='_compute_vat')
    

        
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        group = self.group
        self.tax_id = group.tax_id and group.tax_id.id
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value

#     @api.onchange('od_product_id')
#     def onchange_product_id(self):
#         if self.od_product_id.id:
#             product_obj = self.od_product_id
#             self.name = product_obj.name
#             self.unit_cost = product_obj.standard_price
#     @api.onchange('qty','unit_price')
#     def onchange_unit_price(self):
#         if self.unit_price:
#             self.line_price = self.qty * self.unit_price
#     @api.onchange('qty','unit_cost')
#     def onchange_unit_cost(self):
#         if self.unit_cost:
#             self.line_cost = self.qty * self.unit_cost
#     @api.onchange('line_price','line_cost')
#     def onchange_prices_to_profit(self):
#         self.profit = self.line_price - self.line_cost
#
#     @api.onchange('line_price','profit')
#     def onchange_profit_per(self):
#         if self.line_price:
#             self.profit_percentage = (self.profit/self.line_price)*100
#
#     @api.onchange('group','unit_cost')
#     def onchange_group(self):
#
#         if self.group:
#             profit = self.group.profit /100
#             discount = self.group.customer_discount/100
#             unit_cost = self.unit_cost
#             unit_price = unit_cost + (unit_cost*profit - unit_cost*discount)
#             self.unit_price = unit_price


class od_cost_omn_out_remedial_maintenance_line(models.Model):
    _name = 'od.cost.omn.out.remedial.maintenance.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)
    @api.one
    @api.depends('qty','unit_price','unit_cost','line_price','line_cost','group')
    def compute_calc(self):
        if self.group:
            profit = self.group.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%self.group.name)
            discount = self.group.customer_discount/100
            unit_cost = self.unit_cost
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.unit_price = unit_price
        if self.unit_price and self.qty:
            self.line_price = self.qty * self.unit_price
        if self.unit_cost and self.qty:
            self.line_cost = self.qty * self.unit_cost
        if self.line_price :
            self.profit = self.line_price - self.line_cost
            self.profit_percentage = (self.profit/self.line_price)*100

    
    
    @api.one 
    @api.depends('tax_id','line_price','qty')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value1 = self.line_price * vat
            self.vat_value = vat_value1

    
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    sheet_id = fields.Many2one('od.cost.sheet',string="Sheet")
    item = fields.Char(string='Item')
    name = fields.Char(string='Description')
    qty = fields.Float(string='Qty',default=1)
    unit_price = fields.Float(string='Unit Price',compute='compute_calc')
    line_price = fields.Float(string='Line Price',compute='compute_calc')
    unit_cost = fields.Float(string='Unit Cost')
    line_cost = fields.Float(string='Line Cost',compute='compute_calc')
    profit = fields.Float(string='Profit',compute='compute_calc')
    profit_percentage = fields.Float(string='Profit(%)',compute='compute_calc')
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group')
    show_to_customer = fields.Boolean(string='Show to Customer')
    tax_id = fields.Many2one('account.tax',string="Tax")
    vat = fields.Float(string="VAT %",compute='_compute_vat')
    vat_value = fields.Float(string="VAT Value",compute='_compute_vat')
    
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        group = self.group
        self.tax_id = group.tax_id and group.tax_id.id
    
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value



#     @api.onchange('qty','unit_price')
#     def onchange_unit_price(self):
#         if self.unit_price:
#             self.line_price = self.qty * self.unit_price
#     @api.onchange('qty','unit_cost')
#     def onchange_unit_cost(self):
#         if self.unit_cost:
#             self.line_cost = self.qty * self.unit_cost
#     @api.onchange('line_price','line_cost')
#     def onchange_prices_to_profit(self):
#         self.profit = self.line_price - self.line_cost
#
#     @api.onchange('line_price','profit')
#     def onchange_profit_per(self):
#         if self.line_price:
#             self.profit_percentage = (self.profit/self.line_price)*100
#
#     @api.onchange('group','unit_cost')
#     def onchange_group(self):
#
#         if self.group:
#             profit = self.group.profit /100
#             discount = self.group.customer_discount/100
#             unit_cost = self.unit_cost
#             unit_price = unit_cost + (unit_cost*profit - unit_cost*discount)
#             self.unit_price = unit_price




class od_cost_omn_spare_parts_line(models.Model):
    _name = 'od.cost.omn.spare.parts.line'
    _inherit = 'od.cost.mat.main.pro.line'


class od_cost_omn_maintenance_extra_expense_line(models.Model):
    _name = 'od.cost.omn.maintenance.extra.expense.line'
    _inherit = 'od.cost.mat.extra.expense.line'
    
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        group = self.group
        self.vat = group.vat
    
    @api.one 
    @api.onchange('vat','line_price')
    def onchange_vat(self):
        vat = self.vat
        line_price = self.line_price
        vat_value = line_price * (vat/100.0)
        self.vat_value = vat_value
#     cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
#     item = fields.Char(string='Item')
#     name = fields.Char(string='Description')
#     qty = fields.Float(string='Qty')
#     unit_cost = fields.Float(string='Unit Cost')
#     line_cost = fields.Float(string='Line Cost')
#     show_to_customer = fields.Boolean(string='Show to Customer')




class od_cost_bmn_it_preventive_line(models.Model):
    _name = 'od.cost.bmn.it.preventive.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)

    @api.one
    @api.depends('qty','unit_price','unit_cost','line_price','line_cost','group')
    def compute_calc(self):
        if self.group:
            profit = self.group.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%self.group.name)
            discount = self.group.customer_discount/100
            unit_cost = self.unit_cost
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.unit_price = unit_price
        if self.unit_price and self.qty:
            self.line_price = self.qty * self.unit_price
        if self.unit_cost and self.qty:
            self.line_cost = self.qty * self.unit_cost
        if self.line_price:
            self.profit = self.line_price - self.line_cost
            self.profit_percentage = (self.profit/self.line_price)*100
    
    

    @api.one 
    @api.depends('tax_id','line_price','qty')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value1 = self.line_price * vat
            self.vat_value = vat_value1

    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    sheet_id = fields.Many2one('od.cost.sheet',string="sheet")
    item = fields.Char(string='Item')
    od_product_id = fields.Many2one('product.product',string='Product')
    name = fields.Char(string='Description')
#     imp_code = fields.Many2one('od.implementation',string="Description")
    imp_code = fields.Many2one('od.implementation',string="Description")
    description = fields.Char(string="Description")
    qty = fields.Float(string='Qty',default=1)
    unit_price = fields.Float(string='Unit Price',compute='compute_calc')
    line_price = fields.Float(string='Line Price',compute='compute_calc')
    unit_cost = fields.Float(string='Unit Cost')
    line_cost = fields.Float(string='Line Cost',compute='compute_calc')
    profit = fields.Float(string='Profit',compute='compute_calc')
    profit_percentage = fields.Float(string='Profit(%)',compute='compute_calc')
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group')
    show_to_customer = fields.Boolean(string='Show to Customer')
    tax_id = fields.Many2one('account.tax',string="Tax")
    vat = fields.Float(string="VAT %",compute='_compute_vat')
    vat_value = fields.Float(string="VAT Value",compute='_compute_vat')
    
    
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        group = self.group
        self.tax_id = group.tax_id and group.tax_id.id
    
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value
#     @api.onchange('od_product_id')
#     def onchange_product_id(self):
#         if self.od_product_id.id:
#             product_obj = self.od_product_id
#             self.name = product_obj.name
#             self.unit_cost = product_obj.standard_price
#     @api.onchange('qty','unit_price')
#     def onchange_unit_price(self):
#         if self.unit_price:
#             self.line_price = self.qty * self.unit_price
#     @api.onchange('qty','unit_cost')
#     def onchange_unit_cost(self):
#         if self.unit_cost:
#             self.line_cost = self.qty * self.unit_cost
#     @api.onchange('line_price','line_cost')
#     def onchange_prices_to_profit(self):
#         self.profit = self.line_price - self.line_cost
#
#     @api.onchange('line_price','profit')
#     def onchange_profit_per(self):
#         if self.line_price:
#             self.profit_percentage = (self.profit/self.line_price)*100
#     @api.onchange('group','unit_cost')
#     def onchange_group(self):
#
#         if self.group:
#             profit = self.group.profit /100
#             discount = self.group.customer_discount/100
#             unit_cost = self.unit_cost
#             unit_price = unit_cost + (unit_cost*profit - unit_cost*discount)
#             self.unit_price = unit_price

class od_cost_bmn_it_remedial_line(models.Model):
    _name = 'od.cost.bmn.it.remedial.line'
    _order = "item_int ASC"
    item_int = fields.Integer(string="Item Seq",default=1)

    @api.one
    @api.depends('qty','unit_price','unit_cost','line_price','line_cost','group')
    def compute_calc(self):
        if self.group:
            profit = self.group.profit /100
            if profit >=1:
                raise Warning("Profit value for the costgroup %s set 100 or above,it should be below 100"%self.group.name)
            discount = self.group.customer_discount/100
            unit_cost = self.unit_cost
#             unit_price = (unit_cost / (1-profit)) - (unit_cost * discount)
            unit_price = (unit_cost / (1-profit))
            unit_price = unit_price * (1-discount)
            self.unit_price = unit_price
        if self.unit_price and self.qty:
            self.line_price = self.qty * self.unit_price
        if self.unit_cost and self.qty:
            self.line_cost = self.qty * self.unit_cost
        if self.line_price :
            self.profit = self.line_price - self.line_cost
            self.profit_percentage = (self.profit/self.line_price)*100
    
    @api.one 
    @api.depends('tax_id','line_price','qty')
    def _compute_vat(self):
        if self.tax_id:
            vat = self.tax_id.amount 
            self.vat = vat  * 100
            vat_value1 = self.line_price * vat
            self.vat_value = vat_value1
    
    cost_sheet_id = fields.Many2one('od.cost.sheet',string='Cost Sheet',ondelete='cascade',)
    sheet_id = fields.Many2one('od.cost.sheet',string="sheet")
    item = fields.Char(string='Item')
    name = fields.Char(string='Description')
    qty = fields.Float(string='Qty',default=1)
    unit_price = fields.Float(string='Unit Price',compute='compute_calc')
    line_price = fields.Float(string='Line Price',compute='compute_calc')
    unit_cost = fields.Float(string='Unit Cost')
    line_cost = fields.Float(string='Line Cost',compute='compute_calc')
    profit = fields.Float(string='Profit',compute='compute_calc')
    profit_percentage = fields.Float(string='Profit(%)',compute='compute_calc')
    group = fields.Many2one('od.cost.costgroup.it.service.line',string='Group')
    show_to_customer = fields.Boolean(string='Show to Customer')
    tax_id = fields.Many2one('account.tax',string="Tax")
    vat = fields.Float(string="VAT %",compute='_compute_vat')
    vat_value = fields.Float(string="VAT Value",compute='_compute_vat')
    
    

    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        group = self.group
        self.tax_id = group.tax_id and group.tax_id.id    
#     @api.one 
#     @api.onchange('vat','line_price')
#     def onchange_vat(self):
#         vat = self.vat
#         line_price = self.line_price
#         vat_value = line_price * (vat/100.0)
#         self.vat_value = vat_value
#
#     @api.onchange('qty','unit_price')
#     def onchange_unit_price(self):
#         if self.unit_price:
#             self.line_price = self.qty * self.unit_price
#     @api.onchange('qty','unit_cost')
#     def onchange_unit_cost(self):
#         if self.unit_cost:
#             self.line_cost = self.qty * self.unit_cost
#     @api.onchange('line_price','line_cost')
#     def onchange_prices_to_profit(self):
#         self.profit = self.line_price - self.line_cost
#
#     @api.onchange('line_price','profit')
#     def onchange_profit_per(self):
#         if self.line_price:
#             self.profit_percentage = (self.profit/self.line_price)*100
#     @api.onchange('group','unit_cost')
#     def onchange_group(self):
#
#         if self.group:
#             profit = self.group.profit /100
#             discount = self.group.customer_discount/100
#             unit_cost = self.unit_cost
#             unit_price = unit_cost + (unit_cost*profit - unit_cost*discount)
#             self.unit_price = unit_price



class od_cost_bmn_spareparts_beta_it_maintenance_line(models.Model):
    _name = 'od.cost.bmn.spareparts.beta.it.maintenance.line'
    _inherit = 'od.cost.mat.main.pro.line'


class od_cost_bmn_beta_it_maintenance_extra_expense_line(models.Model):
    _name = 'od.cost.bmn.beta.it.maintenance.extra.expense.line'
    _inherit = 'od.cost.mat.extra.expense.line'
   
    
    
    @api.one 
    @api.onchange('group')
    def onchange_group(self):
        group = self.group
        self.vat = group.vat
    
    @api.one 
    @api.onchange('vat','line_price')
    def onchange_vat(self):
        vat = self.vat
        line_price = self.line_price
        vat_value = line_price * (vat/100.0)
        self.vat_value = vat_value
