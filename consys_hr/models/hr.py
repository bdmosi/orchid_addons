from openerp.osv import fields,osv


class hr_employee(osv.osv):
	_inherit = "hr.employee"
	_columns = {
        'lang_ids': fields.one2many('hr.emloyee.langauage', 'employee_id', 'languages'),
        'family_ids': fields.one2many('hr.employee.family', 'employee_id', 'Family'),
        'academic_ids': fields.one2many('hr.employee.academic', 'employee_id', 'Academic'),
        'project_ids': fields.one2many('hr.employee.project', 'employee_id', 'Project'),
        'history_ids': fields.one2many('hr.emp.history', 'employee_id', 'Employment History'),
        'consyst_ids': fields.one2many('hr.employee.consyst', 'employee_id', 'People You Know at Consyst'),
        'present_address':fields.text('Present Address'),
        'permanent_address':fields.text('Permanent Address'),
        'blood_group':fields.char('Blood Group'),
        'religion':fields.char('Religion'),
        'health':fields.text('Health'),
        'em_contact':fields.char('Emergency Contact Name'),
        'em_relation':fields.char('Relation'),
        'em_contact_no':fields.char('Contact No'),
        'total_experience':fields.text('Total Experience'),
        'report_structure':fields.text('Specify Reporting structure of your position/department in your present /last organisation'),
		'considered':fields.boolean('Have you been considered for employment in Consyst?'),
		'position':fields.char('Position'),
		'date_today':fields.date('Date'),
    }
	def cs_form_fill_mail(self, cr, uid, ids, context=None):
		ir_model_data = self.pool.get('ir.model.data')
		email_obj = self.pool.get('email.template')
		template_id = ir_model_data.get_object_reference(cr, uid, 'consyshr', 'cs_emp_form_fill_email_template')[1]
		employee_record = self.browse(cr, uid, ids)[0]
		if employee_record.work_email:
			email_obj.send_mail(cr, uid, template_id, employee_record.id, force_send=True)
hr_employee()

class hr_employee_langauage(osv.osv):
	_name = "hr.emloyee.langauage"
	_columns = {
			'langauage': fields.char('Language'),
			'can_speak':fields.char('Can Speak'),
			'can_read': fields.char('Can Read'),
			'can_write': fields.char('Can Write'),
			'employee_id': fields.many2one('hr.employee', 'Employee')
			}
hr_employee_langauage()

class hr_employee_family(osv.osv):
	_name = "hr.employee.family"
	_columns = {
			'name':fields.char('Name'),
			'relationship':fields.char('Relationship'),
			'age':fields.char('Age'),
			'occupation':fields.char('Occupation/Organization'),
			'dependent':fields.char('Dependent(Y/N)'),
			'employee_id': fields.many2one('hr.employee', 'Employee')
			}
hr_employee_family()

class hr_employee_academic(osv.osv):
	_name = "hr.employee.academic"
	_columns = {
			'from_date':fields.date('From'),
			'to':fields.date('To'),
			'degree':fields.char('Degree/Deploma'),
			'occupation':fields.char('Occupation/Organization'),
			'college':fields.char('College/University'),
			'subjects': fields.char('subjects'),
			'mark':fields.char("Mark/Grade"),
			'regular':fields.char('Regular/Corresponding'),
			'employee_id': fields.many2one('hr.employee', 'Employee')
			}
hr_employee_academic()

class hr_employee_project(osv.osv):
	_name = "hr.employee.project"
	_columns = {
			'from_date':fields.date('From'),
			'to':fields.date('To'),
			'institution':fields.char('Institution/Organization'),
			'area':fields.char('Area/Topic Covered'),
			'employee_id': fields.many2one('hr.employee', 'Employee')
			}
hr_employee_project()

class hr_emp_history(osv.osv):
	_name = "hr.emp.history"
	_columns = {
			'from_date':fields.date('From'),
			'to':fields.date('To'),
			'tot_exp':fields.char('Total Experience'),
			'address':fields.char('Address of Organization'),
			'job_position':fields.char('Job Position'),
			'nature':fields.char('Basic Nature of Duty'),
			'designation1':fields.char('Designation(On Joining)'),
			'designation2':fields.char('Designation(On Leaving)'),
			'salary1':fields.char('Salary(On Joining)'),
		    'salary2':fields.char('Salary(On Leaving)'),
		    'employee_id': fields.many2one('hr.employee', 'Employee')
			}
hr_emp_history()
class hr_employee_consyst(osv.osv):
	_name = "hr.employee.consyst"
	_columns = {
			'name':fields.char('Name'),
			'employee_id': fields.many2one('hr.employee', 'Employee')
			}

class hr_department(osv.osv):
	_inherit ='hr.department'
	_columns = {
			'resource_requset_ids':fields.one2many('resource.request.line', 'department_id', 'Request Lines'),
			}
hr_department()

class resource_request_line(osv.osv):
	_name='resource.request.line'
	_columns = {'department_id':fields.many2one('hr.department','Department'),
				'name':fields.char('Job Name',required=True),
				'no_of_employee':fields.integer('No Of Employee Required'),
				'approved_no':fields.integer('No of Employee Approved',readonly=True),
				'state':fields.selection([('draft','Draft'),('requested','Waiting For Approval'),('approved','Approved'),('hired','Hired')],'State',readonly=True)
			}
	_defaults = {
				'state':'draft',
				}
	def create_job(self,cr,uid,ids,context=None):
		name = self.browse(cr,uid,ids,context=context).name
		no_of_employee = self.browse(cr,uid,ids,context=context).no_of_employee
		dep_id = self.browse(cr,uid,ids,context=context).department_id.id
		if name:
			vals ={'name':name,'no_of_employee':no_of_employee,'department_id':dep_id,'req_line_id':ids[0]}
			self.pool.get('request.receiver').create(cr,uid,vals,context=context)
			self.write(cr,uid,ids,{'state':'requested'})
		return True
	
resource_request_line()

