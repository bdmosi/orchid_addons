# -*- coding: utf-8 -*-
from openerp.osv import fields,osv
from openerp.tools.translate import _
class crm_lead(osv.osv):
    _inherit = 'crm.lead'
    _columns = {
        'od_approval_state': fields.selection([('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                                 string=' Approval'),
        'od_bdm_user_id': fields.many2one('res.users', 'BDM', select=True, track_visibility='onchange',help="Business Development Manager"),
        'od_responsible_id': fields.many2one('res.users', 'Pre Sales', select=True, track_visibility='onchange',help=" User now handling"),

        'od_lead_bdm_user_id': fields.many2one('res.users', 'Lead BDM', select=True, track_visibility='onchange',help=" Lead Business Development Manager"),
        'od_lead_responsible_id': fields.many2one('res.users', 'Lead Pre Sales', select=True, track_visibility='onchange',help="Lead User now handling"),
        'user_id': fields.many2one('res.users', 'SAM', select=True, track_visibility='onchange',help="Sales Account Manager"),
        'date_deadline': fields.date('Date Deadline', help="Estimate of the date on which the opportunity will be won."),
        'date_action': fields.date('Expectd Booking'),
        'od_branch_id':fields.many2one('od.cost.branch',string='Branch'),
        'od_division_id':fields.many2one('od.cost.division',string='Division'),
    }
    
    
    
    
    def _default_branch(self, cr, uid, context=None):
        res = False
        employee = self.pool.get('hr.employee')
        emp_ids = employee.search(cr, uid, [('user_id','=',uid)], context=context)
        emp_id = emp_ids and emp_ids[0]
        if emp_id:
            emp_obj = employee.browse(cr,uid,emp_id)
            res = emp_obj.od_branch_id and emp_obj.od_branch_id.id
            
        return res
    def _default_division(self, cr, uid, context=None):
        res = False
        employee = self.pool.get('hr.employee')
        emp_ids = employee.search(cr, uid, [('user_id','=',uid)], context=context)
        emp_id = emp_ids and emp_ids[0]
        if emp_id:
            emp_obj = employee.browse(cr,uid,emp_id)
            res = emp_obj.od_division_id and emp_obj.od_division_id.id
            
        return res
    _defaults = {
        'od_approval_state':'pending',
        'user_id':lambda self, cr, uid, context=None: uid,
        'od_branch_id': _default_branch,
        'od_division_id': _default_division,
    }
    def _convert_opportunity_data(self, cr, uid, lead, customer, section_id=False, context=None):
        res=super(crm_lead,self)._convert_opportunity_data(cr, uid, lead, customer, section_id, context=context)
        res.update({'od_bdm_user_id':lead.od_lead_bdm_user_id and lead.od_lead_bdm_user_id.id,
                    'od_responsible_id':lead.od_lead_responsible_id and lead.od_lead_responsible_id.id
                    })
        return res


#     def od_get_user_from_default(self,cr,uid,context=None):
#         val_obj = self.pool.get('ir.values')
#         model = 'crm.model'
#         key = 'default'
#         name ='user_id'
#         user_id =False
#         val_ids =val_obj.search(cr,uid,[('name','=',name)])
#         if val_ids:
#             val_data = val_obj.browse(cr,uid,val_ids[0])
#             user_id = val_data.value_unpickle
#         return user_id
#
#     def default_get(self, cr, uid, fields, context=None):
#         res = super(crm_lead, self).default_get(cr, uid, fields, context=context)
#         print "resssssssssssssssssssssssssssssss default get",res
#         print "user id>>>>>>>>>>>>>>>>>>>>>>",self.od_get_user_from_default(cr, uid, context)
#         user_id = self.od_get_user_from_default(cr, uid, context)
#         res.update({'user_id':int(user_id)})
#         return res

    def copy(self, cr, uid, id, default=None, context=None):
        default = dict(context or {})
        crm = self.browse(cr, uid, id, context=context)
        default.update(
           { 'od_approval_state':'pending'}
           )
        return super(crm_lead, self).copy(cr, uid, id, default, context=context)
    def unlink(self, cr, uid, ids, context=None):
        for data in self.browse(cr, uid, ids, context=context):
            if data.od_approval_state != 'pending':
                raise osv.except_osv(_('Error!'), _('You Can Only Delete Pending state Opportunity'))
        return super(crm_lead, self).unlink(cr, uid, ids, context=context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
