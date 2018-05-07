# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import Warning
class crm_lead(models.Model):
    _inherit = "crm.lead"
    def get_saudi_company_id(self):
        parameter_obj = self.env['ir.config_parameter']
        key =[('key', '=', 'od_beta_saudi_co')]
        company_param = parameter_obj.search(key)
        if not company_param:
            raise Warning(_('Settings Warning!'),_('No Company Parameter Not defined\nconfig it in System Parameters with od_beta_saudi_co!'))
        saudi_company_id = company_param.od_model_id and company_param.od_model_id.id or False
        return saudi_company_id

    def od_send_mail(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        saudi_comp =self.get_saudi_company_id()
        user_company_id = self.env.user.company_id.id
        if user_company_id == saudi_comp:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference('orchid_beta', template)[1]
        crm_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,crm_id, force_send=True)
        return True
    
    @api.multi 
    def write(self,vals):
        if self._uid !=1 and self.od_branch_id and vals.get('od_branch_id'):
            raise Warning("You Cannot Change Branch")
        if self._uid !=1 and self.partner_id and vals.get('partner_id'):
            raise Warning("You Cannot change Customer/Organization")
        return super(crm_lead,self).write(vals)

    @api.one
    def od_approve(self):
        self.od_send_mail('od_crm_approve_mail')
        self.signal_workflow('approve')
    @api.one
    def od_reject(self):
        self.od_send_mail('od_crm_reject_mail')
        self.signal_workflow('reject')
