from openerp.osv import fields,osv
from openerp.tools.translate import _

class request_wiz(osv.osv_memory):
	_name = 'request.wiz'
	_columns = {
		'name':fields.char('Job Name',required=True),
		'no_of_employee':fields.integer('Expected Employees Count'),
			}
	def create_job(self,cr,uid,ids,context=None):
		name = self.browse(cr,uid,ids,context=context).name
		no_of_employee = self.browse(cr,uid,ids,context=context).no_of_employee
		active_id = context.get('active_id')
		if name:
			vals ={'name':name,'no_of_employee':no_of_employee,'department_id':active_id}
			self.pool.get('request.receiver').create(cr,uid,vals,context=context)
			vals1 = {'department_id':active_id,'name':name,'no_of_employee':no_of_employee,'state':'requested'}
			self.pool.get('resource.request.line').create(cr,uid,vals1,context=context)
		return True
