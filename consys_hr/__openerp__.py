# -*- coding: utf-8 -*-
{

	'name': 'Consyst HR',
	'version': '1.0',
	'category': 'HR',
	'sequence': 1,
	'summary': 'Consyst HR',
	'author': 'Jamshid K(jamshu.mkd@gmail.com)',
	'website': 'https://intconsyst.com',
	'depends': ['base','hr','hr_recruitment','website_hr_recruitment','mail'],
	'data': [
			
			'security/consyst_hr_security.xml',
			'security/ir.model.access.csv',
			'views/request_wiz.xml',
			'views/hr.xml',
			'views/menu.xml',
			'views/resource_receiver.xml',
			'views/solution_wiz.xml',
			'views/issue_tracker.xml',
# 			'views/related_issues.xml',
			 'views/issue_solutions.xml',
			 'views/reason_wiz.xml',
			 'views/hr_requirement.xml',
			 'data/issue_sequence.xml',
			 'data/hr_req_seq.xml',
			 'data/cs_template.xml',
			 'views/hr_applicant.xml',
			 'views/templates.xml',
			 'views/form_fill_template.xml',
			
			 
			 ],
	
	
	'installable': True,
	'auto_install': False,
	'application': True,

}
