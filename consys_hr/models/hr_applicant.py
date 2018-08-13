from openerp.osv import fields,osv
from datetime import datetime
from dateutil import parser
from openerp import tools
from openerp import SUPERUSER_ID

from openerp.tools.translate import _
class hr_applicant(osv.osv):
	_inherit = 'hr.applicant'
	_columns = {
			'dob':fields.date('Date Of Birth'),
			'qualification':fields.char('Qualification'),
			'age':fields.char('Age'),
			'gender':fields.selection([('male','Male'),('female','Female')],'Gender'),
			'current_location':fields.char('Current Location'),
			'specialization':fields.char('Specialization'),
			'year':fields.char('Year'),
			'college':fields.char('College'),
			'university':fields.char('University'),
			'experience':fields.selection([('fresher','Fresher'),('experienced','Experienced')],'Experience'),
			'workedat':fields.char('Worked At'),
			'skills':fields.char('Skills'),
			'roll':fields.char('Role'),
			'workexp':fields.char('Work Experience'),
			'notice_period':fields.char('Current Employer Notice Period'),
			'current_ctc':fields.char('Current CTC'),
			'expected_ctc':fields.char('Expected CTC'),
			
			}
	def create_employee_from_applicant(self, cr, uid, ids, context=None):
		""" Create an hr.employee from the hr.applicants """
		if context is None:
			context = {}
		hr_employee = self.pool.get('hr.employee')
		model_data = self.pool.get('ir.model.data')
		act_window = self.pool.get('ir.actions.act_window')
		emp_id = False
		for applicant in self.browse(cr, uid, ids, context=context):
			address_id = contact_name = False
			if applicant.partner_id:
				address_id = self.pool.get('res.partner').address_get(cr, uid, [applicant.partner_id.id], ['contact'])['contact']
				contact_name = self.pool.get('res.partner').name_get(cr, uid, [applicant.partner_id.id])[0][1]
			if applicant.job_id and (applicant.partner_name or contact_name):
				applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1}, context=context)
				create_ctx = dict(context, mail_broadcast=True)
				emp_id = hr_employee.create(cr, uid, {'name': applicant.partner_name or contact_name,
													 'job_id': applicant.job_id.id,
													 'address_home_id': address_id,
													 'department_id': applicant.department_id.id or False,
													 'address_id': applicant.company_id and applicant.company_id.partner_id and applicant.company_id.partner_id.id or False,
													 'work_email': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.email or False,
													 'work_phone': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.phone or False,
													 'mobile_phone':applicant.partner_mobile,
													 'gender':applicant.gender,
													 'birthday':applicant.dob
													 }, context=create_ctx)
				self.write(cr, uid, [applicant.id], {'emp_id': emp_id}, context=context)
				self.pool['hr.job'].message_post(
					cr, uid, [applicant.job_id.id],
					body=_('New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
					subtype="hr_recruitment.mt_job_applicant_hired", context=context)
			else:
				raise osv.except_osv(_('Warning!'), _('You must define an Applied Job and a Contact Name for this applicant.'))

		action_model, action_id = model_data.get_object_reference(cr, uid, 'hr', 'open_view_employee_list')
		dict_act_window = act_window.read(cr, uid, [action_id], [])[0]
		if emp_id:
			dict_act_window['res_id'] = emp_id
		dict_act_window['view_mode'] = 'form,tree'
		return dict_act_window

	def onchange_getage(self,cr,uid,ids,dob,context=None):
		print "haiiiiiiiiiiiiiiiiiiiiiiii"
		current_date=datetime.now()
		current_year=current_date.year
		birth_date = parser.parse(dob)
		current_age=current_year-birth_date.year
		print "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",current_year,birth_date.year,current_age
		val = {
	        'age':str(current_age)
	    }
		return {'value': val}
	
	def cs_approval_mail(self, cr, uid, ids, context=None):
		ir_model_data = self.pool.get('ir.model.data')
		email_obj = self.pool.get('email.template')
		template_id = ir_model_data.get_object_reference(cr, uid, 'consyshr', 'cs_emp_hiring_email_template')[1]
		holiday_record = self.browse(cr, uid, ids)[0]
		if holiday_record.email_from:
			email_obj.send_mail(cr, uid, template_id, holiday_record.id, force_send=True)
# 	def onchange_stage_id(self, cr, uid, ids, stage_id, context=None):
# 		ir_model_data = self.pool.get('ir.model.data')
# 		email_obj = self.pool.get('email.template')
# 		if stage_id == 2:
# 			print "your are at first interview"
# 			template_id = ir_model_data.get_object_reference(cr, uid, 'consyshr', 'cs_emp_hiring_email_template')[1]
# 			email_obj.send_mail(cr, uid, template_id, ids[0], force_send=True)
# 				
# 		if stage_id == 3:
# 			print "your are at Second interview"
# 		return super(hr_applicant,self).onchange_stage_id(cr, uid, ids, stage_id, context=context)



hr_applicant()
