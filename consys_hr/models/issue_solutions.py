from openerp.osv import fields,osv
from openerp.tools.translate import _
class issue_solutions(osv.osv):
	_name = 'issue.solutions'
	_description = 'Solution'
	_inherit = ['mail.thread']
	_columns = {
		'name':fields.char('Name'),
		'issue_id':fields.many2one('issue.tracker','Reference Issue'),
		'date':fields.date('Date'),
		'solution':fields.text('Reply'),
		'attachment':fields.binary('Attachment'),
		'solution_from':fields.many2one('res.users','Reply From',readonly=True),
		'solution_to':fields.many2one('res.users','Reply To'),
		'solution_type':fields.selection([('normal','Normal'),('confidential','Confidential')],'Type',readonly=True,states={'draft': [('readonly', False)]}),
			}
	_defaults = {
				'solution_from': lambda self, cr, uid, ctx=None: self.pool['res.users'].browse(cr, uid, uid, context=ctx).id,
				'date': fields.date.context_today,
				'solution_type':'normal',
				}
	def open_me(self,cr,uid,ids,context=None):
		return {
               
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'issue.solutions',
                'view_id': False,
                'res_id': ids[0],
                'type': 'ir.actions.act_window',
                'target': 'new'
            }
issue_solutions()
