import openerp.exceptions
from openerp.osv import fields, osv, expression

class res_users(osv.osv):
    _inherit = 'res.users'
    _columns = {
        'od_sales_team_ids': fields.many2many('crm.case.section', 'sale_member_rel','member_id', 'section_id',  'Team Members'),
    }
       
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if args is None:
            args = []
        if context is None:
            context={}
        if context.get('sam_ids',False):
            company_id = self.browse(cr, uid, uid, context=context).company_id.id
            team_pool = self.pool.get('crm.case.section')
            team_ids = team_pool.search(cr, uid,  [('user_id.company_id', '=', company_id)], context=context)
            user_ids = []
            for team_id in team_ids:
                team = team_pool.browse(cr,uid,team_id)
                for memb in team.member_ids:
                    user_ids.append(memb.id)
            user_ids = list(set(user_ids))
            if name:
                ids = self.search(cr, uid, [('name', operator, name),('id','in',user_ids)] + args, limit=limit, context=context or {})
            else:
                ids = user_ids
            return self.name_get(cr, uid, ids, context=context)

        return super(res_users, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)



