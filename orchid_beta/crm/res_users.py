import openerp.exceptions
from openerp.osv import fields, osv, expression

class res_users(osv.osv):
    _inherit = 'res.users'
    _columns = {
        'od_sales_team_ids': fields.many2many('crm.case.section', 'sale_member_rel','member_id', 'section_id',  'Team Members'),
    }


