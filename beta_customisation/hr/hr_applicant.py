# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _

class hr_applicant(models.Model):
    _inherit = "hr.applicant"
    
    beta_join_id = fields.Many2one('od.beta.joining.form',string="Beta Joining Form")
    manager_id = fields.Many2one('hr.employee', string="Manager")
    
    def od_send_mail(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        saudi_comp =6
        user_company_id = self.env.user.company_id.id
        if user_company_id == saudi_comp:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference('beta_customisation', template)[1]
        crm_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,crm_id, force_send=True)
        return True
    
    @api.one
    def create_joining_form(self):
        """ Create an od.beta.joining.form from the hr.applicants """
        beta_joining_form = self.env['od.beta.joining.form']
        model_data = self.env['ir.model.data']
        act_window = self.env['ir.actions.act_window']
        emp_id = False
        for applicant in self:
            beta_join_id = beta_joining_form.create({'name': applicant.partner_name,
                                                     'personal_email': applicant.email_from,
                                                     'job_id': applicant.job_id and applicant.job_id.id or False,
                                                     'department_id': applicant.department_id and applicant.department_id.id or False,
                                                     'manager_id': applicant.manager_id and applicant.manager_id.id or False
                                                 })
            self.write({'beta_join_id': beta_join_id.id})
            self.od_send_mail('od_fill_detail_employee')
            return beta_join_id