from openerp.osv import fields,osv
from openerp.tools.translate import _

class skill_data(osv.osv):
	_name = 'skill.data'
	_description ="Skill Data"
	_columns = {
			'name':fields.char('Skill'),
			}

class hr_requirement(osv.osv):
	_name = 'hr.requirement'
	_description = 'Hr Requirement'
	_inherit = ['mail.thread']
	STATES =[('draft','Draft'),
			('sendtoHR','Send To Hr'),
			('sendtoCFO','Send To CFO'),
			('sendtoCEO','Send To CEO'),
			('refused','Refused'),
			('approved','Approved'),
			]
	
	_columns = {
		'name': fields.char('Reference', required=True, copy=False,
            readonly=True,select=True),
		'job_position':fields.char('Job Position'),
		'date_of_request':fields.date('Date of Request',required=True,readonly=True),
		'department_id':fields.many2one('hr.department','Department',required=True),
		'job_desc':fields.text('Job description'),
		#'job_requirement':fields.many2many('skill.data','skill_data_req','req_id', 'skill_id','Requirement'),
		'requirement':fields.text('Requirement'),
		'expected_date':fields.date('Expected Date'),
		'required_count':fields.integer('Required Count'),
		'requested_by':fields.many2one('res.users','Requested By',readonly=True),
		'recruiter_id':fields.many2one('res.users','Recruiter'),
		'state':fields.selection([('draft','Draft'),
			('sendtoHR','Send To Hr'),
			('waitingforapproval','Waiting For Approval'),
			('refused','Refused'),
			('approved','Approved'),
			],'Status'),
		'suggestion':fields.char('Suggestion'),
		#for hr edit fields
		'job_position1':fields.char('Job Position'),
		'department_id1':fields.many2one('hr.department','Department'),
		'job_desc1':fields.text('Job description'),
		'requirement1':fields.text('Requirement'),
		'required_count1':fields.integer('Required Count'),
		'hide_original':fields.boolean('Hide Original Doc'),
		'refuse_reason':fields.text('Reason For Refusal'),
		'refused_by':fields.many2one('res.users','Refused By'),
		
		
		
			}
	_defaults = {
				
				 'state':'draft',
				 'name': lambda obj, cr, uid, context: '/',
				'date_of_request':fields.date.context_today,
				'department_id':lambda self, cr, uid, c: self.get_department(cr, uid,context=c),
				'requested_by':lambda self, cr, uid, ctx=None: self.pool['res.users'].browse(cr, uid, uid, context=ctx).id,
				}
	
	
	
	def prepare_plan(self,cr,uid,ids,context=None):
		for x in self.browse(cr,uid,ids):
			name = x.job_position1
			department_id = x.department_id1.id	
			description = x.job_desc1
			requirements = x.requirement1
			no_of_recruitment = x.required_count1
		if name:
			vals ={'name':name,'department_id':department_id,'description':description,'requirements':requirements,'no_of_recruitment':no_of_recruitment,'user_id':uid}
			res_id=self.pool.get('hr.job').create(cr,uid,vals,context=context)
		if res_id:
			return {
	                'view_type': 'form',
	                'view_mode': 'form',
	                'res_model': 'hr.job',
	                'view_id': False,
	                'res_id': res_id,
	                'type': 'ir.actions.act_window',
	                'target': 'new'
				}
		return True
	def onchange_job_position(self, cr, uid, ids,job_position, context=None):
		result = {}
		result['job_position1'] = job_position
		return {'value': result}
	def onchange_department(self, cr, uid, ids,department_id=False, context=None):
		result = {}
		result['department_id1'] = department_id
		return {'value': result}
	def onchange_job_desc(self, cr, uid, ids,job_desc, context=None):
		result = {}
		result['job_desc1'] = job_desc
		return {'value': result}
	def onchange_requirement(self, cr, uid, ids,requirement, context=None):
		result = {}
		result['requirement1'] = requirement
		return {'value': result}
	def onchange_count(self, cr, uid, ids,required_count, context=None):
		result = {}
		result['required_count1'] = required_count
		return {'value': result}
	
	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if vals.get('name', '/') == '/':
			seq = self.pool.get('ir.sequence').get(cr, uid, 'hr.requirement') or '/'
			spt = seq.split('/')
			vals['name'] = spt[0]+'/'+spt[1][2:]+'/'+spt[2]+'/'+spt[3]+'/'+spt[4]
		return super(hr_requirement,self).create(cr, uid, vals, context=context)
	
	
	def approve_by_hr(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'waitingforapproval','hide_original':True},context=context)
	def refuse_by_hr(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'refused'},context=context)
	def send_to_hr(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'sendtoHR'},context=context)
	def approve(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'approved'},context=context)
	def refuse(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'refused'},context=context)
	
	def get_department(self,cr,uid,context=None):
		emp_obj = self.pool.get('hr.employee')
		emp_ids = emp_obj.search(cr,uid,[('user_id','=',uid)],context=context)
		if emp_ids:
			emp_id = emp_ids[0]
			return emp_obj.browse(cr,uid,emp_id,context=context).department_id.id
		return False
	
	
		
	
hr_requirement()
