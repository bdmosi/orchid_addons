import time
import datetime
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api, _


class BetaJoiningForm(models.Model):
    _name = 'od.beta.joining.form'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Beta Joining Form"
    
    name  = fields.Char(string='Employee Name', track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('cancel', 'Terminated')],
                                  string='State', readonly=True,
                                  track_visibility='always', copy=False,  default= 'draft')
    work_email = fields.Char(string='Work Email')
    department_id = fields.Many2one('hr.department', string='Department') 
    job_id = fields.Many2one('hr.job', string='Job Title')
    manager_id = fields.Many2one('hr.employee', string='Manager')
    coach_id = fields.Many2one('hr.employee', string='Coach')
    nationality = fields.Many2one('res.country', string='Nationality')
    dob = fields.Date(string='Date of Birth')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Gender')
    joining_date = fields.Date(string='Joining Date', track_visibility='onchange')
    branch_id = fields.Many2one('od.cost.branch', string='Branch')
    tech_dept_id = fields.Many2one('od.cost.division', string='Technology Unit/Department')
    cost_centre_id = fields.Many2one('od.cost.centre', string='Cost Centre')
    pay_salary_during_annual_leave = fields.Boolean('Pay Salary During Annual Leave')
    
    type_id = fields.Many2one('hr.contract.type', string='Contract Type')
    mode_of_pay_id = fields.Many2one('od.mode.of.payment', string='Mode of Payment')
    total_wage = fields.Float(string="Total Wage")
    basic_wage = fields.Float(string="Basic Wage")
    allowance_rule_line_ids = fields.One2many('allowance.rule.line','joining_id','Rule Lines')
    salary_struct = fields.Many2one('hr.payroll.structure', string='Salary Structure')
    
    work_sched = fields.Many2one('resource.calendar', string='Working Schedule')
    work_hrs = fields.Integer(string="Working Hours")
    schedule_pay = fields.Selection([
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('semi-annually', 'Semi-annually'),
            ('annually', 'Annually'),
            ('weekly', 'Weekly'),
            ('bi-weekly', 'Bi-weekly'),
            ('bi-monthly', 'Bi-monthly'),
            ], 'Scheduled Pay', select=True, default="monthly")
    journal_id = fields.Many2one('account.journal', string='Salary Journal')
    manager1_id = fields.Many2one('res.users', string='First Approval Manager(Leaves)')
    manager2_id = fields.Many2one('res.users', string='Second Approval Manager(Leaves)')
    audit_temp_id = fields.Many2one('audit.template', string='Audit Template')
    
    def get_emp_vals(self):
        vals = { 'name' : self.name,
                'work_email': self.work_email,
                'department_id': self.department_id and self.department_id.id or False,
                'job_id': self.job_id and self.job_id.id or False,
                'parent_id': self.manager_id and self.manager_id.id or False,
                'coach_id': self.coach_id and self.coach_id.id or False,
                'country_id': self.nationality and self.nationality.id or False,
                'birthday': self.dob,
                'gender': self.gender,
                'active': True,
                'od_joining_date': self.joining_date,
                'od_pay_salary_during_annual_leave': self.pay_salary_during_annual_leave,
                'od_branch_id': self.branch_id and self.branch_id.id or False,
                'od_division_id': self.tech_dept_id and self.tech_dept_id.id or False,
                'od_cost_centre_id': self.cost_centre_id and self.cost_centre_id.id or False,
                'od_based_on_basic': True,
                'od_first_manager_id': self.manager1_id and self.manager1_id.id or False,
                'od_second_manager_id': self.manager2_id and self.manager2_id.id or False,
            }
        return vals
        
        
    
    
    @api.model 
    def create_employee(self):
        employee_pool = self.env['hr.employee']
        vals = self.get_emp_vals()
        emp_id = employee_pool.create(vals)
        return emp_id
    
    @api.model
    def create_contract(self, emp_id):
        contract_pool = self.env['hr.contract']
        date_start_dt = fields.Datetime.from_string(self.joining_date)
        company_id = self.env.user.company_id or False
        if company_id == 6:
            dt = date_start_dt + relativedelta(months=3)
        else:
            dt = date_start_dt + relativedelta(months=6)
        
        vals = {'name': self.name,
                'employee_id': emp_id.id,
                'job_id': self.job_id and self.job_id.id or False,
                'od_active': True,
                'type_id': self.type_id and self.type_id.id or False,
                'xo_mode_of_payment_id': self.mode_of_pay_id and self.mode_of_pay_id.id or False,
                'xo_total_wage': self.total_wage,
                'wage': self.basic_wage,
                'struct_id': self.salary_struct and self.salary_struct.id or False,
                'xo_allowance_rule_line_ids': [(0, 0, {'rule_type':x.rule_type.id,'amt':x.amt}) for x in self.allowance_rule_line_ids],
                'trial_date_start': self.joining_date,
                'trial_date_end': fields.Datetime.to_string(dt),
                'date_start': self.joining_date,
                'working_hours': self.work_sched and self.work_sched.id or False,
                'xo_working_hours': self.work_hrs,
                'schedule_pay': self.schedule_pay,
                'journal_id': self.journal_id and self.journal_id.id or False
            }
        
        contract_id = contract_pool.create(vals)
        return contract_id
    
    @api.model
    def create_user(self):
        user_pool = self.env['res.users']
        field_list = user_pool.fields_get_keys()
        default_vals = user_pool.default_get(field_list) #This One need for default values needed for create user
        
        name_list = self.name.split()
        first_name = name_list[0] or ''
        last_name = name_list[-1] or ''
        vals = {'name' : first_name.capitalize() + ' ' + last_name.capitalize(),
                'login' : self.work_email,
            }
        default_vals.update(vals)
        user_id = user_pool.create(default_vals)
        return user_id
    
    @api.one
    @api.model
    def confirm_emp(self):
        emp_id = self.create_employee()
        contract_id = self.create_contract(emp_id)
        user_id = self.create_user()
        emp_id.write({'user_id': user_id and user_id.id or False, 'address_home_id': user_id.partner_id and user_id.partner_id.id or False})
        self.state = 'confirm'
        return emp_id
    
    @api.one
    @api.model
    def cancel_emp(self):
        emp_rec = self.env['hr.employee'].search([('name','=',self.name),('active','=',True)])
        emp_rec.write({'active': False})
        contract_rec = self.env['hr.contract'].search([('name','=',self.name),('od_active','=',True)])
        contract_rec.write({'od_active': False})
        users_rec = self.env['res.users'].search([('login','=',self.work_email),('active','=',True)])
        users_rec.write({'active': False})
        self.state = 'cancel'

class allowance_rule_line(models.Model):
    _inherit = 'allowance.rule.line'
    
    joining_id = fields.Many2one('od.beta.joining.form', string='Joining ID', ondelete='cascade')
    
    
class hr_payroll_structure(models.Model):
    _inherit = 'hr.payroll.structure'
    
    joining_id = fields.Many2one('od.beta.joining.form', string='Joining ID', ondelete='cascade')

    