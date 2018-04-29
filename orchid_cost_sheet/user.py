from openerp.osv import fields,osv 


class res_users(osv.osv):
    _inherit = 'res.users'
    
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if args is None:
            args = []
        if context is None:
            context={}
        if context.get('sam_ids',False):
            company_id = self.browse(cr, uid, uid, context=context).company_id.id
            team_pool = self.pool.get('crm.case.section')
            team_ids = team_pool.search(cr, uid,  [('company_id', '=', company_id)], context=context)
            user_ids = []
            for team_id in team_ids:
                team = team_pool.browse(cr,uid,team_id)
                for memb in team.member_ids:
                    user_ids.append(memb.id)
            user_ids = list(set(user_ids))
            return self.name_get(cr, uid, user_ids, context=context)

        return super(res_users, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)
