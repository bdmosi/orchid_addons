from openerp.osv import fields,osv

class related_issues(osv.osv):
	_name = 'related.issues'
	_description = 'Common Issues'
	_columns = {
		'name':fields.char('Name'),
# 		'symptoms':fields.text('Symptoms'),
# 		'solutions':fields.text('Solutions'),
			}
related_issues()
