from openerp.osv import fields,osv,orm
from openerp.tools.translate import _

class reason_wiz(osv.osv_memory):
	_name = 'reason.wiz'
	_columns = {
		'reason':fields.text('Reason'),
			}
	def enter_reason(self,cr,uid,ids,context=None):
		reason = self.browse(cr,uid,ids,context=context).reason
		active_id = context.get('active_id')
		if reason:
			vals ={'refuse_reason':reason,'state':'refused','refused_by':uid}
			self.pool.get('hr.requirement').write(cr,uid,active_id,vals,context=context)
		return True
