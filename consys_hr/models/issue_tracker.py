from openerp.osv import fields,osv
from openerp.tools.translate import _



class issue_tracker(osv.osv):
	_name = 'issue.tracker'
	_description = "Issue Tracker"
	_inherit = ['mail.thread']
	_columns = {
		 'name': fields.char('Issue Reference', required=True, copy=False,
            readonly=True,select=True),
		'subject':fields.char('Subject'),
		'from_id':fields.many2one('res.users','From',readonly=True),
		'to':fields.many2many('res.users','ticket_user_rel','ticket_id','user_id','Followers',required=True),
		'date':fields.date('Date'),
		'Description':fields.text('Description'),
		'related_model':fields.char('Related Model'),
		'ref':fields.integer('Reference ID'),
		'attachment':fields.binary('Attachment'),
		'tag_ids': fields.many2many('related.issues', 'issue_rel_tag', 'issue_id', 'tag_id', 'Related Tags'),
		'solution_ids':fields.one2many('issue.solutions','issue_id','Suggested Solutions',readonly=True),
		'state':fields.selection([('draft','Draft'),('open','Open'),('replied','Replied'),('closed','Closed')],'Status'),
		'issue_type':fields.selection([('normal','Normal'),('confidential','Confidential')],'Type',readonly=True,states={'draft': [('readonly', False)]}),
			}
	_defaults = {
				'from_id': lambda self, cr, uid, ctx=None: self.pool['res.users'].browse(cr, uid, uid, context=ctx).id,
				 'date': fields.date.context_today,
				 'state':'draft',
				 'issue_type':'normal',
				 'name': lambda obj, cr, uid, context: '/',
				}
	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if vals.get('name', '/') == '/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'issue.tracker') or '/'
		return super(issue_tracker,self).create(cr, uid, vals, context=context)
			
	
	def open(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids,{'state':'open'},context=context)
		for x in self.browse(cr,uid,ids,context=context):
			print "dddddddddddddddddddddddddd",x.to
		return True
		
	def close(self,cr,uid,ids,context=None):
		from_id = self.browse(cr,uid,ids,context=context).from_id.id
		if uid == from_id:
			self.write(cr,uid,ids,{'state':'closed'},context=context)
		else:
			raise osv.except_osv(_('Invalid Action!'),
                                     _('You cannot Close this ticket'))
		
	def reopen(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids,{'state':'open'},context=context)
	def open_doc(self,cr,uid,ids,context=None):
		for x in self.browse(cr, uid, ids, context=context):
			model = x.related_model
			res_id = x.ref
		if model and res_id:
			return {
	                'view_type': 'form',
	                'view_mode': 'form',
	                'res_model': model,
	                'view_id': False,
	                'res_id': res_id,
	                'type': 'ir.actions.act_window',
	                'target': 'new'
				}
		return True
issue_tracker()


