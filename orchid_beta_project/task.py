# -*- coding: utf-8 -*-
from openerp import models, fields, api,_
from datetime import datetime,timedelta,date
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import decimal
from openerp.exceptions import Warning
from pprint import pprint
from openerp.tools import SUPERUSER_ID

class od_kind_of_work(models.Model):
    _name = 'od.kind.of.work'
    name = fields.Char(string="Kind of Work")

class task(models.Model):
    _inherit = 'project.task'
    
    
   
    
    
    def check_audit_period(self):
        today = date.today()
        year = today.year
        month = today.month 
        day = today.day 
        if day >26:
            month = month +1
        audit_end = str(year)+'-'+str(month)+'-'+str(26)
        audit_end = datetime.strptime(audit_end,'%Y-%m-%d')
        task_end_date = self.date_end 
        task_end_date = datetime.strptime(task_end_date,DEFAULT_SERVER_DATETIME_FORMAT)
        if task_end_date > audit_end:
            return True
        return False
    
    @api.one 
    @api.depends('date_start','od_implementation_id','date_end')
    def x_get_end_date(self):
#         duration = self.od_implementation_id and self.od_implementation_id.expected_act_duration
        duration = self.planned_hours
        self.b_plan_hr = duration 
        date_start = self.date_start
        
#         if date_start:
#             date_start = datetime.strptime(date_start, DEFAULT_SERVER_DATETIME_FORMAT)
#             dt = date_start + timedelta(hours=duration or 0.0)
#             dt_s = dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
#             self.date_end = dt_s 
#         date_end = self.date_end
        self.b_date_end = self.date_end
    @api.multi 
    def btn_cancel_by_tl(self):
        if self.check_audit_period():
            self.unlink()
        else:
            self.work_ids.unlink()
            self.od_stage ='cancel_by_tl'
            self.cancel_tl_id = self._uid
    
    @api.multi 
    def btn_cancel_by_owner(self):
        if self.check_audit_period():
            name = self.name +': Cancelled By Owner'
            cancelled_by_id = self._uid
            cancelled_by_owner = True 
            narration ='Cancelled By Owner'
            user_id = self.user_id and self.user_id.id or False 
            hours = self.planned_hours 
            date = self.date_start
            task_id = self.id
            vals = {
                'name':name,'user_id':user_id,'hours':hours,'date':date,'cancelled_by_id':cancelled_by_id,
                'cancelled_by_owner':cancelled_by_owner,'narration':narration,'task_id':task_id
                
                }
            self.env['project.task.work']._create_analytic_entries(vals)
            self.unlink()
        else:
            self.unlink()   
    
    def od_milestone_escalation_schedule(self,cr,uid,context=None):
        print "milestone escalation schedule starded"
        today = date.today()
        today = datetime.strftime(today,DEFAULT_SERVER_DATETIME_FORMAT)
        data_ids = self.search(cr,uid,[])
        for data in self.browse(cr,uid,data_ids):
            deadline = data.date_end
            if deadline < today and (data.od_stage != 'done') and data.od_type == 'milestone':
                print "task with tak id>>>>>>>>>>>>>>>>>>>>>>>",data.id
                template = 'od_milestone_escalation_template'
                self.od_send_mail_old_api(cr, uid, data.id, template)
    def get_time_diff(self,start_time,complete_time):
        start_time = datetime.strptime(start_time, DEFAULT_SERVER_DATETIME_FORMAT)
        complete_time = datetime.strptime(complete_time, DEFAULT_SERVER_DATETIME_FORMAT)
        diff = (complete_time -start_time)
        days = diff.days * 24
        seconds = diff.seconds
        hour= days + float(seconds)/3600
        return hour
    def get_day_diff(self,start_time,complete_time):
        start_time = datetime.strptime(start_time, DEFAULT_SERVER_DATETIME_FORMAT)
        complete_time = datetime.strptime(complete_time, DEFAULT_SERVER_DATETIME_FORMAT)
        diff = (complete_time -start_time)
        days = diff.days
        return days
    @api.constrains('work_ids')
    def od_check_work(self):
        if self.od_type == 'activities':
            date_start = self.date_start
            if len(self.work_ids) > 1:
                raise Warning("Only One work for a Task,Please Remove Extra Work,Maintain One work Only")
            for work in self.work_ids:
                work_start = work.date
                if date_start and work_start:
                    day_diff = self.get_day_diff(date_start,work_start)
                    print "day diff>>>>>>>>>>>>>>>>>>>>>>>>>>>",day_diff
                    if day_diff > 1 :
                        raise Warning("Please Check Work Start time and Task Start Time ,It should be under 24 hour Range")
    def od_create_calendar_event(self,vals):
        context = self._context
        if context.get('default_od_type',False) == 'activities':
            duration = self.get_time_diff(vals['date_start'],vals['date_end'])
            project_id = vals.get('project_id',False)
            project_pool = self.env['project.project']
            project_obj = project_pool.browse(project_id)
            analytic_account_id = project_obj.analytic_account_id and project_obj.analytic_account_id.id or False
            meeting_vals = {
                'name': '   ' + vals['name'],
                'categ_ids': vals['categ_ids'] or [],
                'duration': duration,
                'description': vals['name'],
                'user_id': vals['user_id'],
                'partner_ids': vals['partner_ids'],
                'start': vals['date_start'],
                'stop': vals['date_end'],
                'od_analytic_account_id':analytic_account_id,
                'allday': False,
                'state': 'open',            # to block that meeting date in the calendar
                'class': 'confidential'
            }
            calendar = self.env['calendar.event']
            meeting_id = calendar.create(meeting_vals)
            return meeting_id.id
        return False

    
    @api.one
    def copy(self, default):
        
        #add your code here
        default.update({'od_duplicated':True,'od_write_count':0,
                        'od_stage':'draft','od_date_done':False,
                        'od_quality_of_implementation':False,
                        'od_quality_of_documentation':False,
                        'od_complexiety':False,'od_overnight':False,
                        'od_outstation':False,'od_owner_esc_time':False,
                        'od_owner_res_time':False,
                        'od_owner_esc_status':False,
                        'od_own_esc':False
                        
                        })
        print "default>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",default
        return super(task, self).copy(default)
    
    def create_task_line(self,vals):
        date_start = vals.get('date_start')
        status = 'completed'
        name = vals.get('name','/')
        locked = True
        user_id = vals.get('user_id')
        vals =[(0,0,{'date':date_start,'state':status,'locked':locked,'user_id':user_id,'name':name,'hours':0.0})]
        return vals
    
    @api.model
    def create(self,vals):
        self.check_task_user_overlap(vals)
        project_id = vals.get('project_id')
        project_obj = self.env['project.project'].browse(project_id)
        state = project_obj.state
        od_type = self.od_type
        print "od_type>>>>>>>>>>>>>>>>>>>>>>",od_type,vals
        if state in ('cancelled','close'):
            raise Warning("This Project Either Cancelled or Closed,You Cant Create a task for this Project")
        meeting_id =self.od_create_calendar_event(vals)
        vals['od_meeting_id'] = meeting_id
        if not vals.get('od_duplicate',False):
            vals['od_block_start'] = True
        if vals.get('od_type') not in ('milestone','workpackage'):
            work_ids =self.sudo().create_task_line(vals)
            vals['work_ids'] = work_ids
        return super(task,self).create(vals)

    def get_saudi_company_id(self):
        parameter_obj = self.env['ir.config_parameter']
        key =[('key', '=', 'od_beta_saudi_co')]
        company_param = parameter_obj.search(key)
        if not company_param:
            raise Warning(_('Settings Warning!'),_('No Company Parameter Not defined\nconfig it in System Parameters with od_beta_saudi_co!'))
        saudi_company_id = company_param.od_model_id and company_param.od_model_id.id or False
        return saudi_company_id
    
    
    
    def od_send_mail_old_api(self,cr,uid,ids,template):
        print "trying to send mail"
        ir_model_data = self.pool['ir.model.data']
        email_obj = self.pool.get('email.template')
        template_id = ir_model_data.get_object_reference(cr,uid,'orchid_beta_project', template)[1]
        print "emila temlp id>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",template_id
        email_obj.send_mail(cr,uid,template_id,ids, force_send=True)
        return True
    
    
    def od_send_mail(self,template):
        ir_model_data = self.env['ir.model.data']
        email_obj = self.pool.get('email.template')
        saudi_comp =self.get_saudi_company_id()
        if self.company_id.id == saudi_comp:
            template = template +'_saudi'
        template_id = ir_model_data.get_object_reference('orchid_beta_project', template)[1]
        task_id = self.id
        email_obj.send_mail(self.env.cr,self.env.uid,template_id,task_id, force_send=True)
        return True
    
    def write_on_work(self,date_done):
#         date_done = datetime.strftime(datetime.now(),DEFAULT_SERVER_DATETIME_FORMAT)
        date_start = self.date_start
        
        for line in self.work_ids:
            if not line.od_complete_date:
                raise Warning("You Need to Enter the Complete Date on Work Tab")
            if line.locked:
                duration = self.get_time_diff(date_start,line.od_complete_date)
                line.write({'date':date_start,})
    
    
    
    def check_activity_report(self):
        if not (self.od_initial_description and self.od_final_result and self.od_action_taken):
            raise Warning("Activity Report Not Completed!!!!!")
    
    def check_work_line(self):
        if not self.work_ids:
            raise Warning("Please Fill the Work Tab")
    
    @api.one
    def btn_done(self):
        
        date_done = datetime.strftime(datetime.now(),DEFAULT_SERVER_DATETIME_FORMAT)
        self.check_activity_report()
        if self.od_type == 'activities':
            self.check_list_status()
            self.check_work_line()
        self.od_date_done = date_done
        self.write_on_work(date_done)
        self.od_send_mail('od_task_done_mail')
        
        self.write({'od_stage':'done','stage_id':1})

    @api.one
    def btn_cancel(self):
        self.od_date_done = ''
        # self.write({'od_stage':'cancel'})

    @api.one
    def btn_reset(self):
        self.od_date_done = ''
        self.write({'od_stage':'draft','stage_id':15})

    @api.one
    def unlink(self):
        if self.no_delete:
            raise Warning("This Task Blocked to Delete")
        if self.od_child_ids:
            raise Warning("Milestone/Workpackages Cannot be Deleted if they have Child Tasks")
        self.od_send_mail('od_task_delete_mail')
        if self.od_meeting_id:
            self.od_meeting_id.unlink()
        return super(task,self).unlink()
    def default_get(self, cr, uid, fields, context=None):
        project_pool = self.pool.get('project.project')
        res = super(task, self).default_get(cr, uid, fields, context=context)
        partner_id = res.get('partner_id',False)
        res['od_common_partner_id'] = partner_id
        od_type = res.get('od_type',False)
        if od_type in ('milestone','workpackage'):
            project_id = context.get('default_project_id',False)
            if project_id:
                project_obj = project_pool.browse(cr,uid,project_id)
                owner_id = project_obj.user_id and  project_obj.user_id.id
                res['user_id'] = owner_id
                if  od_type == 'milestone':
                    date_start = project_obj.date_start
                    date_end = project_obj.date
                    res['date_start'] = date_start
                    res['date_end'] = date_end
                    type_of_project = project_obj.od_type_of_project
                    if type_of_project == 'amc':
                        res['od_state'] = 8
                    elif type_of_project == 'o_m':
                        res['od_state'] = 9
                    else:
                        res['od_state'] = 1
        return res

    @api.multi
    def btn_assign_user(self):
        context = self._context
        ctx = {'task_id':self.id}
        ctx.update(context)
        result = {
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'wiz.assign.user',
              'type': 'ir.actions.act_window',
              'target': 'new',
              'context': ctx
              }
        return result
    def od_technical_eval_change(self,vals):
        if vals.get('od_quality_of_implementation'):
            return True
        if vals.get('od_quality_of_documentation'):
            return True
        if vals.get('od_complexiety'):
            return True
        if vals.get('od_overnight'):
            return True
        if vals.get('od_outstation'):
            return True
        if vals.get('od_consultant_comment'):
            return True
        return False
    def od_owner_eval_change(self,vals):
        if vals.get('od_owner_approval'):
            return True
        if vals.get('od_satisfaction'):
            return True
        return False
    @api.one
    @api.depends('od_depend_task_lines')
    def od_get_max_end_date(self):
        if self.od_type in ('workpackage','milestone'):
            date_list = []
            for line in self.od_depend_task_lines:
                if line.condition == 'end_to_start':
                    date_list.append(line.date_end)
                else:
                    date_list.append(line.date_start)
            if date_list:
                self.od_max_date = max(date_list)
                self.date_start = max(date_list)

    
    def edit_block(self,vals):
        super_pass = self.b_super_pass 
        if not super_pass:
            write_count_check =2
            if self.od_duplicated:
                write_count_check =3
            if self.od_type == 'activities' and self.od_write_count >=write_count_check:
                if vals.get('date_start') or vals.get('planned_hours') or vals.get('date_end'):
                    raise Warning("You Cannot Change Starting Date, Planned Hours or Complete Date, Please press the Discard Button")
        
    @api.multi
    def write(self, vals):
        ctx = self.env.context
        print "my cccctx>>>>>>>>>>>>>>>>>>>>>>888888xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx>>>>",ctx
        
        self.edit_block(vals)
#         if vals.get('user_id'):
#             self.check_task_user_overlap(vals)
        
        tech_check = self.od_technical_eval_change(vals)
        owner_check = self.od_owner_eval_change(vals)
        uid =self._uid
        date = str(datetime.now())
        res =[{'evaluated_by':uid,'date':date}]

        if tech_check:
            self.od_tech_eval_log_ids = res
        if owner_check:
            self.od_owner_eval_log_ids = res
        cal_val = {}
        if vals.get('date_start',False):
            cal_val['start'] = vals['date_start']
        if vals.get('date_end',False):
            cal_val['stop'] = vals['date_end']
        if vals.get('user_id',False):
            cal_val['user_id'] = vals['user_id']
        if vals.get('partner_ids',False):
            cal_val['partner_ids'] = vals['partner_ids']
        if vals.get('categ_ids',False):
            cal_val['categ_ids'] = vals['categ_ids']
        if cal_val:
            meeting_id = self.od_meeting_id
            if meeting_id:
                meeting_id.write(cal_val)
#         date_start = self.date_start
#         if not vals.get('date_start',False):
#             vals['date_start'] = date_start
#         vals['od_block_start'] = True
        
#         vals['od_duplicated'] = False
        write_count = self.od_write_count + 1
        vals['od_write_count'] =write_count
        if write_count >=3:
            vals['od_duplicated'] =False
        return super(task, self).write(vals)
#     @api.constrains('user_id','date_start','date_end')
#     def check_task_conflict(self):
#         od_type = self.od_type
#         if od_type == 'activities':
#             task = self.env['project.task']
#             user_id = self.user_id and self.user_id.id
#             date_start = self.date_start
#             date_end = self.date_end
#             dom = [('user_id','=',user_id),('date_start','>=',date_start),('date_start','<=',date_end)]
#             tasks = task.search(dom)
#             task_ids = [tk.id for tk in tasks]
#             if len(tasks)>1:
#                 raise Warning("This User Assigned Another Task in This Time with these %s Active  Task Ids "%task_ids)
    
    
    def check_task_user_overlap(self,vals):
        imp_cod = vals.get('od_implementation_id',False)
        if imp_cod:
            task = self.env['project.task']
            user_id = vals.get('user_id')
            date_start = vals.get('date_start')
            date_end = vals.get('date_end')
            dom = [('user_id','=',user_id),('date_start','>=',date_start),('date_start','<=',date_end)]
            tasks = task.search(dom)
            for tk in tasks:
                if tk.od_stage =='cancel_by_tl':
                    continue
                elif tk.od_stage =='done' and tk.od_date_done <= date_start:
                    continue
                else:
                    raise Warning("Task Overlap!!!!!This User Assigned Another Task in This Time with these %s Active  Task Ids "%tk.id)
            dom = [('user_id','=',user_id),('date_end','>=',date_start),('date_end','<=',date_end)]
            tasks = task.search(dom)
            for tk in tasks:
                if tk.od_stage =='cancel_by_tl':
                    continue
                elif tk.od_stage =='done' and tk.od_date_done <= date_start:
                    continue
                else:
                    raise Warning("Task Overlap!!!!!This User Assigned Another Task in This Time with these %s Active  Task Ids "%tk.id)
            
            
    @api.constrains('date_start','date_end',)
    def check_date(self):
        if self.od_type == 'milestone':
            project = self.project_id
            project_start = project.date_start
            project_end = project.date
            if self.date_start and self.date_end:
                date_start,time = self.date_start.split(' ')
                date_end,time = self.date_end.split(' ')
                if not ((project_end >= date_start >= project_start) and (project_start <= date_end <= project_end)):
                    raise Warning("Selected Dates/Times Cannot Be Outside Project Time Frame (%s to %s)"%(project_start,project_end))
        if self.od_parent_id:
            if self.od_parent_id and self.od_parent_id.date_start and self.od_parent_id.date_end:
                parent_date_end,time = self.od_parent_id.date_end.split(' ')
                parent_date_start,time = self.od_parent_id.date_start.split(' ')
                if self.date_start and self.date_end:
                    date_end,time = self.date_end.split(' ')
                    date_start,time = self.date_start.split(' ')

            if self.date_start and self.date_end:
                if not ((parent_date_end >= date_start >= parent_date_start) and (parent_date_start <= date_end <= parent_date_end)):
                    raise Warning("Child Task Date Should be Under Parent task Scheduled Date \n Check Date Start and Date End(%s to %s)"%(parent_date_start,parent_date_end))



    @api.constrains('date_start','od_max_date')
    def check_date_start_max_date(self):
        if self.od_type in ('milestone','workpackage'):
            if self.date_start < self.od_max_date :
                raise Warning("Conflict With Dependent Task Date/Time")
    @api.constrains('od_parent_id','od_state','project_id')
    def check_phase_id(self):
        print "my state", self.od_state.id
        if self.od_parent_id:
            print "parent state",self.od_parent_id.od_state.id
            if self.od_state.id != self.od_parent_id.od_state.id:
                raise Warning("Parent and Child task Phase should be Same")
            if self.project_id.id != self.od_parent_id.project_id.id:
                raise Warning("Parent and Child task Project should be Same")

    # @api.constrains('od_checklist_ids')
    def check_list_status(self):
        if self.od_type == 'activities':
            for line in self.od_checklist_ids:
                if not line.state:
                    raise Warning("Please Enter The Status of CheckList")
    @api.onchange('od_parent_id')
    def onchange_parent_id(self):
        if self.od_parent_id:
            od_state = self.od_parent_id and self.od_parent_id.od_state and self.od_parent_id.od_state.id or False
            project_id = self.od_parent_id and self.od_parent_id.project_id and self.od_parent_id.project_id.id or False
            self.od_state = od_state
            self.project_id = project_id



    @api.one
    @api.depends('date_start','planned_hours')
    def _get_od_end_date(self):
        """Compute the End date"""
        res = {}
        for order in self:
            if order.date_deadline:
                date_start = datetime.strptime(order.date_start, DEFAULT_SERVER_DATETIME_FORMAT)
                dt = date_start + timedelta(hours=order.planned_hours or 0.0)
                dt_s = dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                res[order.id] = dt_s
                self.od_end_time = dt_s
                if self.od_type == 'activities':
                    date_start = datetime.strptime(order.date_start, DEFAULT_SERVER_DATETIME_FORMAT)
                    dt_e = date_start + timedelta(hours=order.planned_hours or 0.0)
                    dt_end = dt_e.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                    self.date_end = dt_end


    @api.one
    @api.depends('work_ids')
    def _get_od_actual_time(self):

        hours = 0.0
        for data in self:
            for line in data.work_ids:
                hours += line.hours
        self.od_actual = hours

    @api.one
    @api.depends('planned_hours','od_actual')
    def _get_od_remaining(self):

        planned_hours = self.planned_hours
        actual_time = self.od_actual
        rem = planned_hours - actual_time
        self.od_remaining = rem



    def check_task_cycle(self,data):
        result = []
        for child in data:
            if child.od_type == 'activities':
                result.append(child)
            else:
                for dat in child.od_child_ids:
                    self.check_task_cycle(dat)
        return result




    @api.one
    @api.depends('od_child_ids')

    def _get_total_plan(self):
        results =[]
        def rec_plan(data):
            for child in data:
                if child.od_type == 'activities':
                    results.append(child)
                else:
                    for dat in child.od_child_ids:
                        try:
                            rec_plan(dat)
                        except:
                            raise Warning("Computing Total Time Recurively with Too Many Task... Please Group By With Projects")

            return results
        res = rec_plan(self)
        plan_time =0.0
        for val in res:
            plan_time += val.planned_hours
        self.od_total_planned = plan_time



    @api.one
    @api.depends('od_child_ids')
    def _get_total_remain(self):

        total_planned_hours = self.od_total_planned
        total_time_spent = self.od_total_time_spent
        rem = total_planned_hours - total_time_spent
        self.od_total_remain = rem

    @api.one
    @api.depends('od_child_ids')

    def _get_total_timespent(self):

        results =[]

        def rec_actual(data):
            for child in data:
                if child.od_type == 'activities':
                    results.append(child)
                else:
                    for dat in child.od_child_ids:
                        try:
                            rec_actual(dat)
                        except Exception as e:
                            raise Warning("Computing Total Time Recurively with Too Many Task.... Please Group By With Projects")

            return results

        res = rec_actual(self)
        actual_time =0.0
        for val in res:
            actual_time += val.od_actual
        self.od_total_time_spent = actual_time


    def get_coach_user_id(self,cr,uid,user_id,context):
        uid = SUPERUSER_ID
        hr = self.pool.get('hr.employee')
        coach_user = False
        hr_id=hr.search(cr,uid,[('user_id','=',user_id)],limit=1)
        hr_obj = hr.browse(cr,uid,hr_id,context)
        coach_user=hr_obj.coach_id and  hr_obj.coach_id.user_id and hr_obj.coach_id.user_id.id or False
        return coach_user
        
        

    @api.onchange('user_id')
    def onchange_user_id(self):
        hr = self.env['hr.employee']
        cr = self.env.cr
        uid = self.env.uid
        context = self.env.context
        coach_user = False
        partner_ids = []
        partner_id = self.user_id and self.user_id.partner_id and self.user_id.partner_id.id
        if partner_id:
            partner_ids.append(partner_id)
        if self.user_id:
            user_id = self.user_id.id
            coach_user = self.get_coach_user_id(user_id)
#             if users_list and users_list[0]:
#                 coach_user=users_list[0].coach_id and  users_list[0].coach_id.user_id and users_list[0].coach_id.user_id.id or False

        self.reviewer_id = coach_user
        # self.partner_ids = partner_ids
        self.partner_ids = [[6, False,partner_ids]]
    @api.onchange('od_common_partner_id')
    def onchange_common_partner_id(self):
        partner_ids =[]
        partner_id = self.od_common_partner_id and self.od_common_partner_id.id
        partner_ids.append(partner_id)
        self.partner_ids = partner_ids
    @api.one
    @api.depends('od_date_done')
    def _od_auto_approval(self):

        def min_eval_date(line_id):
            date_list = []
            for line in line_id:
                date_list.append(line.date)
            if date_list:
                print "date list>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",date_list
                return min(date_list)
            return False
        if self.od_date_done and self.od_type == 'activities':
            date_done= datetime.strptime(self.od_date_done,DEFAULT_SERVER_DATETIME_FORMAT)
            date_reach = date_done + timedelta(days=3)
            print "date done>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",date_done
            print "date reach firestttttttttttttttttttttttttttttttttttttttttttttttttttt",date_reach
            eval_date = min_eval_date(self.od_owner_eval_log_ids)
            if eval_date:
                eval_date = datetime.strptime(eval_date,DEFAULT_SERVER_DATETIME_FORMAT)
                print "eval date>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",eval_date
                print "date reach>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",date_reach
                if eval_date > date_reach:
                    self.od_auto_approved = True
                else:
                    self.od_auto_approved = False
            else:
                self.od_auto_approved = True
    @api.one
    @api.depends('od_date_done','date_end')
    def _od_late_eval(self):
        def min_eval_date(line_id):
            date_list = []
            for line in line_id:
                date_list.append(line.date)
            if date_list:
                return min(date_list)
            return False
        if self.od_date_done and self.od_type == 'activities':
            if self.date_end > '2018-04-17':
                date_end= datetime.strptime(self.date_end,DEFAULT_SERVER_DATETIME_FORMAT)
                date_reach = date_end + timedelta(hours=36)
                eval_date = min_eval_date(self.od_tech_eval_log_ids)
                if eval_date:
                    eval_date = datetime.strptime(eval_date,DEFAULT_SERVER_DATETIME_FORMAT)
                    print "eval date>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",eval_date
                    print "date reach>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",date_reach
                    if eval_date > date_reach :
                        self.od_late_in_tech_eval = True
                    else:
                        self.od_late_in_tech_eval = False
#                 if datetime.now() > date_reach and not eval_date:
#                     self.od_late_in_tech_eval = False
    # @api.one
    # def od_submit_task(self):
    #     self.od_status ='submitted'
    # *.xml = fields.Many2one('res.partner',domain=[('is_company','=',True),('customer','=',True)])

    # def _od_partner_id(self):
    #     project_id = self.project_id
    #     partner_id = False
    #     context = self.env.context
    #     if project_id :
    #         partner_id = self.project_id.partner_id
    #     print "project id>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",project_id,partner_id
    #     print "context>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",context
    #     return partner_id
    
    b_plan_hr = fields.Float(string="Planned Hours",compute="x_get_end_date")
    b_date_end = fields.Datetime(string="Ending Date",compute="x_get_end_date")
    b_super_pass = fields.Boolean(string="Super Pass")
    no_delete = fields.Boolean(string="Delete Blocked")
    od_duplicated = fields.Boolean(string="Duplicated")
    od_block_start = fields.Boolean(string="Block Starting Date Edit")
    od_write_count = fields.Integer(string="Write Count")
#     date_start  = fields.Datetime('Starting Date',track_visibility='onchange')
    od_help_desk_issue_id = fields.Many2one('crm.helpdesk',string="Help Desk Issue Sequence")
    od_meeting_id = fields.Many2one('calendar.event',string='Meeting')
    od_stage = fields.Selection([('draft','In Progress'),('done','Done'),('cancel_by_tl','Cancelled By TL')],string="Status",default='draft',track_visibility='onchange')
    cancel_tl_id = fields.Many2one('res.users',string="Cancel TL User")
    od_date_done = fields.Datetime(string="Date Done",readonly=False)
    od_opp_id = fields.Many2one('crm.lead',string="Opportunity")
    od_max_date = fields.Datetime(string="Computational Max Date",compute="od_get_max_end_date")
    od_depend_task_lines = fields.One2many('od.depend.task.lines','depend_task_id',string="Depend Task Lines",ondelete="cascade")
    partner_ids = fields.Many2many('res.partner','rel_od_task_partners','task_id','partner_id', string='Attendees')
    od_owner_id = fields.Many2one('res.users',string="Owner",readonly=True,related="project_id.user_id")
    # od_purchase_count = fields.Integer(string="Purchase Count",compute="od_get_count_purchase")
    od_purchase_id = fields.Many2one('purchase.order',string="Purchase Order")
    od_delivery_order_line = fields.One2many('od.task.delivery.order','task_id',string="Delivery Orders",readonly=True)
    od_material_request = fields.Boolean(string="Material Request")
    od_total_planned = fields.Float(string='Total Planned Hours',compute='_get_total_plan')
    od_total_time_spent = fields.Float(string='Total Time Spent',compute='_get_total_timespent')
    od_total_remain = fields.Float(string="Total Remaining Hours",compute='_get_total_remain')
    # od_end_time = fields.Datetime(string='Planned End Time',compute='_get_od_end_date',store=True)
    od_actual = fields.Float(string='Actual Time Spent',compute='_get_od_actual_time',size=8)
    od_remaining = fields.Float(string='Remaining Time',compute="_get_od_remaining")
    # kind_of_work = fields.Many2one('od.kind.of.work',string="Kind Of Work")
    od_city = fields.Many2one('res.country.state',string="City")
    od_location = fields.Char('Location')
    od_implementation_id =fields.Many2one('od.implementation','Implementation Code')
    od_categ_id = fields.Many2one('od.product.sub.group','Category')
    od_sub_categ_id = fields.Many2one('od.project.sub.category',string="Sub Category")
    od_partner_id = fields.Many2one('res.partner',string="Customer",related="project_id.partner_id",readonly=True)
    od_common_partner_id = fields.Many2one('res.partner',string="Customer")
    od_contact_ids = fields.Many2many('res.partner','od_project_task_rel_contact_ids','task_id','partner_id',string="Contact Person")
    DOM_MAT_STAT = [('material_request','Material Request'),('purchase_order','Purchase Order'),
                    ('goods_received','Goods Received'),('delivery_request','Delivery Request'),
                    ('delivered','Delivered'),
                    ]

    od_material_status = fields.Selection(DOM_MAT_STAT,string="Material Status")
    # STAT = [('draft','New'),('submitted','Submitted')]
    # od_status = fields.Selection(STAT,string="Status",readonly=True,default='draft')
#    Acitvity Report tab
    od_initial_description = fields.Text('Initial Description of Situation')
    od_action_taken = fields.Text('Action Taken')
    od_final_result = fields.Text('Conclusion And Final Result')
#    Technical Evaluation Tab
    od_quality_of_implementation = fields.Selection([('good','Good'),('average','Average'),('poor','Poor')],'Quality of Implementation')
    od_quality_of_documentation = fields.Selection([('good','Good'),('average','Average'),('poor','Poor')],'Quality of Documentation')
    od_complexiety = fields.Selection([('easy','Easy'),('normal','Normal'),('complex','Complex')],'Complexity')
    od_overnight = fields.Boolean('Overnight')
    od_outstation = fields.Boolean('Outstation')
    od_consultant_comment = fields.Text('Consultant Comment')
    od_tech_eval_log_ids = fields.One2many('od.task.technical.eval.log','task_id',string="Technincal Eval Log",readonly=True)

#   Owner Evalutation Tab
    od_owner_approval = fields.Selection([('yes','Yes'),('partial','Partial Achievement'),('no','No')],'Owner Approval')
    od_satisfaction = fields.Float('Satisfaction %')
    od_auto_approved = fields.Boolean('Late In Approval',compute="_od_auto_approval")
    od_late_in_tech_eval = fields.Boolean('Not Evaluated/Late In Evaluation',compute="_od_late_eval")
    od_parent_id = fields.Many2one('project.task','Parent')
    od_by_delegate = fields.Boolean('By Delegate')
    od_owner_eval_log_ids = fields.One2many('od.task.owner.eval.log','task_id',string="Owner Eval Log",readonly=True)

#new Owner evaluation by escalation
    od_owner_esc_time = fields.Datetime(string="Escalation Time",track_visibility='onchange') 
    od_owner_res_time = fields.Datetime(string="Resolution Time",track_visibility='onchange')
    od_owner_esc_status  = fields.Selection([('escalated','Escalated'),('resolved','Resolved'),('not_solved','Not Resolved')],string="Owner Escalation Status",track_visibility='onchange')
    od_own_esc = fields.Boolean(string="Escalated?") 
  
#   Prerequisite
    od_activity_technical_obj = fields.Text(string="Activity Technical Objective")
    od_eqp_application = fields.Text(string="Equipment / Applications")
    od_prior_arrangement = fields.Text(string="Prior Arrangement Required")

# Material Request Line
    od_material_request_line = fields.One2many('od.material.request','task_id',string="Material Request Line")
    material_loaded = fields.Boolean(string="Material Loaded")
#contact person details fields
    od_contact_person_details = fields.Text(string="Details")
    
    @api.multi 
    def btn_owner_esclate(self):
        self.od_own_esc =True
        self.od_owner_esc_status ='escalated'
        self.od_send_mail('od_escalation_mail')
        self.od_owner_esc_time = str(datetime.now())

    @api.multi 
    def btn_owner_resolved(self):
        if self.od_owner_esc_status == 'not_solved':
            raise Warning("24 Hr Time Exceeded to Resolve the Task, Now you cant Resolve this Activity")
        resolve_time = datetime.strftime(datetime.now(),DEFAULT_SERVER_DATETIME_FORMAT)
        escalation_time = self.od_owner_esc_time
        hours = self.get_time_diff(escalation_time, resolve_time)
        if hours > 24:
            self.od_owner_esc_status ='not_solved'
            return True
        self.od_owner_res_time =str(datetime.now())
        self.od_owner_esc_status ='resolved'



#engineer KPI
    @api.one
    @api.depends('od_type','od_actual','planned_hours')
    def _get_time_kpi(self):
        if self.od_type == 'activities':
            planned_hours = self.planned_hours
            actual = self.od_actual
            if actual <= planned_hours:
                self.od_time_kpi = 100
            else:
                self.od_time_kpi = 0

    def get_date_done(self):
        date_done = ''
        for line in self.work_ids:
            date_done  = line.od_complete_date 
#         if not date_done:
#             date_done = self.od_date_done
        return date_done
   
    def check_date_done_on_same_day(self,date_done,date_end):
        if not date_done or not date_end:
            return False
        date_end = datetime.strptime(date_end,DEFAULT_SERVER_DATETIME_FORMAT)
        date_done = datetime.strptime(date_done,DEFAULT_SERVER_DATETIME_FORMAT)
        
        return date_done.day <= date_end.day
    
    
    @api.one
    @api.depends('od_type','date_end','od_date_done')
    def _get_end_kpi(self):
        if self.od_type == 'activities':
            date_end = self.date_end 
            date_done = self.od_date_done
            check_date_done = self.check_date_done_on_same_day(date_done,date_end)
            complete_date = self.get_date_done()
            if complete_date and date_end:
                date_end = datetime.strptime(date_end,DEFAULT_SERVER_DATETIME_FORMAT)
                complete_date = datetime.strptime(complete_date,DEFAULT_SERVER_DATETIME_FORMAT)
                date_end = date_end + timedelta(minutes=5)
                if complete_date and date_end:
                    if (complete_date > date_end) or (not check_date_done) or (self.od_late_in_tech_eval):
                        self.od_end_kpi = 0
                    else:
                        self.od_end_kpi = 60


    @api.one
    @api.depends('od_type','od_quality_of_implementation')
    def _get_quality_kpi(self):
        if self.od_type == 'activities':
            quality = self.od_quality_of_implementation
            if quality == 'good':
                self.od_qualiy_kpi = 20
            elif quality == 'average':
                self.od_qualiy_kpi = 12
            else:
                self.c = 0

    @api.one
    @api.depends('od_type','od_quality_of_documentation')
    def _get_doc_kpi(self):
        if self.od_type == 'activities':
            doc = self.od_quality_of_documentation
            if doc == 'good':
                self.od_doc_kpi = 20
            elif doc == 'average':
                self.od_doc_kpi = 12
            else:
                self.od_doc_kpi = 0

    @api.one
    @api.depends('od_type','od_complexiety')
    def _get_complexiety_kpi(self):
        if self.od_type == 'activities':
            complx = self.od_complexiety
            if complx == 'complex':
                self.od_complexiety_kpi = 5
            elif complx == 'normal':
                self.od_complexiety_kpi = 3
            elif complx == 'easy':
                self.od_complexiety_kpi = 1
            else:
                self.od_complexiety_kpi = 0



    @api.one
    @api.depends('od_type','od_overnight')
    def _get_overnight_kpi(self):

        if self.od_type == "activities" and self.od_overnight:
            self.od_overnight_kpi = 15
        else:
            self.od_overnight_kpi = 0

    @api.one
    @api.depends('od_type','od_outstation')
    def _get_outstation_kpi(self):
        if self.od_type == "activities" and self.od_outstation:
            self.od_outstation_kpi = 15
        else:
            self.od_outstation_kpi = 0
    
    @api.one 
    def _get_kpi_total(self):
        self.od_total_kpi = self.od_end_kpi +self.od_qualiy_kpi + self.od_doc_kpi +self.od_overnight_kpi + self.od_outstation_kpi 
        
    od_total_kpi = fields.Float(string="Total Scores",compute="_get_kpi_total")
    od_time_kpi = fields.Float(string="Time KPI",compute="_get_time_kpi")
    od_end_kpi = fields.Float(string="Planned Done KPI",compute="_get_end_kpi")
    od_qualiy_kpi = fields.Float(string="Quality Points",compute="_get_quality_kpi")
    od_doc_kpi = fields.Float(string="Documentation Points",compute="_get_doc_kpi")
    od_complexiety_kpi = fields.Float(string="Complexiety Points",compute="_get_complexiety_kpi")
    od_overnight_kpi = fields.Float(string="Overnight Point",compute="_get_overnight_kpi")
    od_outstation_kpi = fields.Float(string="Outstation Point",compute="_get_outstation_kpi")
#owner KPI
    @api.one
    @api.depends('od_type','od_auto_approved')
    def _get_owner_kpi(self):
        if self.od_type == 'activities' and not self.od_auto_approved:
            self.od_ownr_eval_kpi = 100
        else:
            self.od_ownr_eval_kpi = 0
    od_ownr_eval_kpi = fields.Float(string="Feedback On Time",compute="_get_owner_kpi")
#Technical Consultant Api
    @api.one
    @api.depends('od_type','od_late_in_tech_eval')
    def _get_technical_kpi(self):
        if self.od_type  == 'activities' and not self.od_late_in_tech_eval:
            self.od_technical_kpi = 100
        else:
            self.od_technical_kpi = 0

    od_technical_kpi = fields.Float(string="Evaluation On Time",compute="_get_technical_kpi")



class od_depend_task_lines(models.Model):
    _name = "od.depend.task.lines"
    _description = "Depend Tasks"
    depend_task_id =  fields.Many2one('project.task',string="Depend Task")
    task_id = fields.Many2one('project.task',string="Task")
    condition = fields.Selection([('start_to_start','Start to Start'),('end_to_start','End To Start')],string="Condition")
    date_start = fields.Datetime(string='Date Start',related="task_id.date_start")
    date_end = fields.Datetime(string="Date End",related="task_id.date_end")
class od_material_request(models.Model):
    _name = 'od.material.request'

    def get_product_domain(self):
        from pprint import pprint
        res = []
        product_ids = []
        context = self._context
        pprint(context)
        params = context.get('params',False)
        project_id =context.get('default_project_id')

        # if params:
        #     print "param>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",params
        #     task_id = params.get('id',False)
        #     print "task_id>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",task_id
        #     project_id =  params.get('active_id',False)
        #     if task_id:
        #         task = self.env['project.task']
        #         task_obj = task.browse(task_id)
        #         project_id = task_obj.project_id and task_obj.project_id.id

        if project_id:
            project = self.env['project.project']
            project_obj = project.browse(project_id)
            for line in project_obj.od_material_budget_line:
                product_ids.append(line.product_id.id)
            res = [('id','in',product_ids)]
        return res
    task_id = fields.Many2one('project.task',string="Task")
    product_id = fields.Many2one('product.product',string="Product",domain=get_product_domain)
    partner_id = fields.Many2one('res.partner',string="Location")
    qty = fields.Float(string='Quantity')
    date = fields.Date(string="Expected Date")
    po = fields.Boolean(string="PO",readonly=True)
    do = fields.Boolean(string="DO",readonly=True)
    state = fields.Selection([('requested','Requested'),('not_requested','Not Requested')],string="Status",default='not_requested',readonly=True)


class od_task_delivery_order(models.Model):
    _name = "od.task.delivery.order"
    task_id = fields.Many2one('project.task',string="Task")
    picking_id = fields.Many2one('stock.picking',string="Delivery Order")

class od_task_technical_eval_log(models.Model):
    _name = "od.task.technical.eval.log"
    task_id = fields.Many2one('project.task',string="Task")
    evaluated_by = fields.Many2one('res.users',string="Evaluated By")
    date = fields.Datetime(string="Date")

class od_task_owner_eval_log(models.Model):
    _name = "od.task.owner.eval.log"
    task_id = fields.Many2one('project.task',string="Task")
    evaluated_by = fields.Many2one('res.users',string="Evaluated By")
    date = fields.Datetime(string="Date")
