from openerp.osv import fields,osv

class request_receiver(osv.osv):
	_description = 'Request'
	_name = 'request.receiver'
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	
	_columns = {
		'name':fields.char('Name'),
		'department_id':fields.many2one('hr.department','Department'),
		'no_of_employee':fields.integer('No_of_employee'),
		'responsible':fields.many2one('res.users','Responsible'),
		'req_line_id':fields.many2one('resource.request.line','Request Line'),
		'state':fields.selection([('draft','Draft'),('refuse','Refused'),('approve','Approved')])
			}
	_defaults = {
				'state':'draft'
			}
	def approve(self,cr,uid,ids,context=None):
		name = self.browse(cr,uid,ids,context=context).name
		no_of_employee = self.browse(cr,uid,ids,context=context).no_of_employee
		department_id = self.browse(cr,uid,ids,context=context).department_id.id
		responsible = self.browse(cr,uid,ids,context=context).responsible.id
		req_line_id = self.browse(cr,uid,ids,context=context).req_line_id.id
		if name:
			vals ={'name':name,'no_of_recruitment':no_of_employee,'department_id':department_id,'user_id':responsible}
			self.pool.get('hr.job').create(cr,uid,vals,context=context)
			self.write(cr,uid,ids,{'state':'approve'})
			self.pool.get('resource.request.line').write(cr,uid,req_line_id,{'state':'approved','approved_no':no_of_employee},context)
request_receiver()
