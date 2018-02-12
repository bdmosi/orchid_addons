from openerp import models, fields, api

class od_issue_log(models.Model):
    _name = 'od.issue.log'
    def od_get_company_id(self):
        return self.env.user.company_id.id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    project_id = fields.Many2one('project.project','Project')
    od_issue_description = fields.Date('Issue Description')
    od_priority =fields.Selection([('low','Low'),('medium','Medium'),('high','High')],'Priority')
    od_date_reported = fields.Date('Date Reported')
    od_reported_by =fields.Char('Reported By')
    od_assigned_to = fields.Many2one('hr.employee','Assigned To')
    od_date_resolved = fields.Date('Date Resolved')
    od_status = fields.Selection([('open','Open'),('progress','In Progress'),('closed','Closed')],'Status')
    od_resolution = fields.Text('Resolution/Comments')

od_issue_log()

class od_risk_log(models.Model):
    _name = 'od.risk.log'
    def od_get_company_id(self):
        return self.env.user.company_id.id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)
    project_id = fields.Many2one('project.project','Project')
    od_risk_description =fields.Char('Risk Description')
    od_date_identified = fields.Date('Date Identified')
    od_impact =fields.Selection([('low','Low'),('medium','Medium'),('high','High')],'Impact')
    od_risk_priority =fields.Selection([('low','Low'),('medium','Medium'),('high','High')],'Priority')
    od_action_taken =fields.Text('Action Taken')
    od_action_needed =fields.Text('Action Needed')
    od_responsible =fields.Many2one('hr.employee','Responsible Person')
    od_risk_status = fields.Selection([('open','Open'),('progress','In Progress'),('closed','Closed')],'Status')

od_risk_log()
class project_project(models.Model):
    _inherit ='project.project'
    od_issue_log_line = fields.One2many('od.issue.log','project_id',string='Issue Log')
    od_risk_log_line = fields.One2many('od.risk.log','project_id',string='Risk Log')