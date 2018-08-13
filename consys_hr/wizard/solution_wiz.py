from openerp.osv import fields,osv,orm
from openerp.tools.translate import _

class solution_wiz(osv.osv_memory):
	_name = 'solution.wiz'
	_description = 'Solution Wizard'
	_columns = {
		'date':fields.date('Date'),
		'solution':fields.text('Reply'),
		'attachment':fields.binary('Attachment'),
		'solution_from':fields.many2one('res.users','Solution From'),
			}
	_defaults = {
				'date':fields.date.context_today,
				'solution_from': lambda self, cr, uid, ctx=None: self.pool['res.users'].browse(cr, uid, uid, context=ctx).id,
				}
	def create_solution(self,cr,uid,ids,context=None):
		c_obj = self.pool.get('issue.tracker')
		s_obj = self.pool.get('issue.solutions')
		c_id = context.get('active_id',False)
		user_list =[]
		
		
		for x in self.browse(cr, uid, ids, context=context):
			date = x.date
			solution = x.solution
			attachment = x.attachment
			solution_from = x.solution_from.id
		for ob in c_obj.browse(cr,uid,c_id,context=context):
			name = ob.name + "'s" + ' Solution'
			solution_to = ob.from_id.id
			solution_type = ob.issue_type
			user_list.append(ob.from_id.id)
			for x in ob.to:
				if x.id:
					user_list.append(x.id)
			if not uid in user_list:
				raise osv.except_osv(_('Error!'), _(' Sorry You Cannot Reply for This Ticket'))
		vals = {
			'name':name,
			'issue_id':c_id,
			'date':date,
			'solution':solution,
			'attachment':attachment,
			'solution_from':solution_from,
			'solution_to':solution_to,
			'solution_type':solution_type,
			}
		if vals:
			s_obj.create(cr,uid,vals,context=context)
			if uid != solution_to:
				c_obj.write(cr,uid,[c_id],{'state':'replied'},context=context)
			else:
				c_obj.write(cr,uid,[c_id],{'state':'open'},context=context)
		
		
		
