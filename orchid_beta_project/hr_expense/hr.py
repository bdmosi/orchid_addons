# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
from openerp.exceptions import Warning
import re
from datetime import date as dt
from datetime import timedelta,datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
class hr_employee(models.Model):
    _inherit ="hr.employee"
    
   
    
    #audit fileds
    audit_temp_id = fields.Many2one('audit.template',string="Audit Template")
    aud_date_start1 = fields.Date(string="Audit Start")
    aud_date_end1 = fields.Date(string="Audit End")
    execute1 = fields.Boolean("Execute")
    weight1 = fields.Float(string="Weight")
    audit_sample1 = fields.Many2one('audit.sample',string="Audit Sample")
    score1  = fields.Float(string="Score")
    cert1 = fields.Boolean(string="Certificate Required")
    cert_id1 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight1 = fields.Float(string="Certificate Weight")
    cert_status1 = fields.Selection([('not_achieved','Not Achieved'),('achieved','Achieved')],string="Certificate Status")
    aud_date_start2 = fields.Date(string="Audit Start")
    aud_date_end2 = fields.Date(string="Audit End")
    execute2 = fields.Boolean("Currently Executing")
    weight2 = fields.Float(string="Weight")
    audit_sample2 = fields.Many2one('audit.sample',string="Audit Sample")
    score2  = fields.Float(string="Score")
    cert2 = fields.Boolean(string="Certificate Required")
    cert_id2 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight2 = fields.Float(string="Certificate Weight")
    cert_status2 = fields.Selection([('not_achieved','Not Achieved'),('achieved','Achieved')],string="Certificate Status")
    
    aud_date_start3 = fields.Date(string="Audit Start")
    aud_date_end3 = fields.Date(string="Audit End")
    execute3 = fields.Boolean("Currently Executing")
    weight3 = fields.Float(string="Weight")
    audit_sample3 = fields.Many2one('audit.sample',string="Audit Sample")
    score3  = fields.Float(string="Score")
    cert3 = fields.Boolean(string="Certificate Required")
    cert_id3 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight3 = fields.Float(string="Certificate Weight")
    cert_status3 = fields.Selection([('not_achieved','Not Achieved'),('achieved','Achieved')],string="Certificate Status")

    
    aud_date_start4 = fields.Date(string="Audit Start")
    aud_date_end4 = fields.Date(string="Audit End")
    execute4 = fields.Boolean("Currently Executing")
    weight4 = fields.Float(string="Weight")
    audit_sample4 = fields.Many2one('audit.sample',string="Audit Sample")
    score4  = fields.Float(string="Score")
    cert4 = fields.Boolean(string="Certificate Required")
    cert_id4 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight4 = fields.Float(string="Certificate Weight")
    cert_status4 = fields.Selection([('not_achieved','Not Achieved'),('achieved','Achieved')],string="Certificate Status")

    
    aud_date_start5 = fields.Date(string="Audit Start")
    aud_date_end5 = fields.Date(string="Audit End")
    execute5 = fields.Boolean("Currently Executing")
    weight5 = fields.Float(string="Weight")
    audit_sample5 = fields.Many2one('audit.sample',string="Audit Sample")
    score5  = fields.Float(string="Score")
    cert5 = fields.Boolean(string="Certificate Required")
    cert_id5 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight5 = fields.Float(string="Certificate Weight")
    cert_status5 = fields.Selection([('not_achieved','Not Achieved'),('achieved','Achieved')],string="Certificate Status")

    
    aud_date_start6 = fields.Date(string="Audit Start")
    aud_date_end6 = fields.Date(string="Audit End")
    execute6 = fields.Boolean("Currently Executing")
    weight6 = fields.Float(string="Weight")
    audit_sample6 = fields.Many2one('audit.sample',string="Audit Sample")
    score6  = fields.Float(string="Score")
    cert6 = fields.Boolean(string="Certificate Required")
    cert_id6 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight6 = fields.Float(string="Certificate Weight")
    cert_status6 = fields.Selection([('not_achieved','Not Achieved'),('achieved','Achieved')],string="Certificate Status")

    
    aud_date_start7 = fields.Date(string="Audit Start")
    aud_date_end7 = fields.Date(string="Audit End")
    execute7 = fields.Boolean("Currently Executing")
    weight7 = fields.Float(string="Weight")
    audit_sample7 = fields.Many2one('audit.sample',string="Audit Sample")
    score7  = fields.Float(string="Score")
    cert7 = fields.Boolean(string="Certificate Required")
    cert_id7 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight7 = fields.Float(string="Certificate Weight")
    cert_status7 = fields.Selection([('not_achieved','Not Achieved'),('achieved','Achieved')],string="Certificate Status")
    
    aud_date_start8 = fields.Date(string="Audit Start")
    aud_date_end8 = fields.Date(string="Audit End")
    execute8 = fields.Boolean("Currently Executing")
    weight8 = fields.Float(string="Weight")
    audit_sample8 = fields.Many2one('audit.sample',string="Audit Sample")
    score8  = fields.Float(string="Score")
    cert8 = fields.Boolean(string="Certificate Required")
    cert_id8 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight8 = fields.Float(string="Certificate Weight")
    cert_status8 = fields.Selection([('not_achieved','Not Achieved'),('achieved','Achieved')],string="Certificate Status")

    
    aud_date_start9 = fields.Date(string="Audit Start")
    aud_date_end9 = fields.Date(string="Audit End")
    execute9 = fields.Boolean("Currently Executing")
    weight9 = fields.Float(string="Weight")
    audit_sample9 = fields.Many2one('audit.sample',string="Audit Sample")
    score9  = fields.Float(string="Score")
    cert9 = fields.Boolean(string="Certificate Required")
    cert_id9 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight9 = fields.Float(string="Certificate Weight")
    cert_status9 = fields.Selection([('not_achieved','Not Achieved'),('achieved','Achieved')],string="Certificate Status")
    
    
    aud_date_start10 = fields.Date(string="Audit Start")
    aud_date_end10 = fields.Date(string="Audit End")
    execute10 = fields.Boolean("Currently Executing")
    weight10 = fields.Float(string="Weight")
    audit_sample10 = fields.Many2one('audit.sample',string="Audit Sample")
    score10  = fields.Float(string="Score")
    cert10 = fields.Boolean(string="Certificate Required")
    cert_id10 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight10 = fields.Float(string="Certificate Weight")
    cert_status10 = fields.Selection([('not_achieved','Not Achieved'),('achieved','Achieved')],string="Certificate Status")

    
    aud_date_start11 = fields.Date(string="Audit Start")
    aud_date_end11 = fields.Date(string="Audit End")
    execute11 = fields.Boolean("Currently Executing")
    weight11 = fields.Float(string="Weight")
    audit_sample11 = fields.Many2one('audit.sample',string="Audit Sample")
    score11  = fields.Float(string="Score")
    cert11 = fields.Boolean(string="Certificate Required")
    cert_id11 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight11 = fields.Float(string="Certificate Weight")
    cert_status11 = fields.Selection([('not_achieved','Not Achieved'),('achieved','Achieved')],string="Certificate Status")
    
    
    aud_date_start12 = fields.Date(string="Audit Start")
    aud_date_end12 = fields.Date(string="Audit End")
    execute12 = fields.Boolean("Currently Executing")
    weight12 = fields.Float(string="Weight")
    audit_sample12 = fields.Many2one('audit.sample',string="Audit Sample")
    score12  = fields.Float(string="Score")
    cert12 = fields.Boolean(string="Certificate Required")
    cert_id12 = fields.Many2one('employee.certificate',string="Certificate")
    cert_weight12 = fields.Float(string="Certificate Weight")
    cert_status12 = fields.Selection([('not_achieved','Not Achieved'),('achieved','Achieved')],string="Certificate Status")
    
    
    
    def get_execution_number(self):
        mstr = 'execute'
        res = {}
        for i in range(1,13):
            fnm =mstr+str(i)
            val =eval('self'+'.'+fnm)
            res[i] = val
        result  =[]
        for key,value in res.iteritems():
            if value:
                result.append(key)
#         if len(result) >1:
#             raise Warning("Only 1 Execution Allowed and At least One Execution Needed ")
        return result[0]
    
    
    def update_audit_sample(self,sample_id,aud_date_start,aud_date_end,audit_temp_id):
        type = audit_temp_id.type
        user_id  = self.user_id and self.user_id.id
        employee_id = self.id
        dt_start = aud_date_start
        result = []
        if type =='post_sales':
            data_model = 'project.task'
            domain = [('od_type','=','activities'),('user_id','=',user_id),('od_stage','=','done')]
            aud_date_start = aud_date_start +' 04:00:00'
            aud_date_end = aud_date_end + ' 23:58:58'
            domain.extend([('date_start','>=',aud_date_start),('date_start','<=',aud_date_end)]) 
            data_ids =self.env[data_model].search(domain)
            for data in data_ids: 
                result.append((0,0,{'task_id':data.id,'score':data.od_total_kpi}))
            sample_id.post_sale_sample_line.unlink()
            sample_id.write({'post_sale_sample_line':result})
        
        if type =='ttl':
            eng_ids = self.search([('coach_id','=',employee_id)]) 
            user_ids = [emp.user_id.id for emp in eng_ids] 
            data_model = 'project.task'
            avl_time = self.get_available_time(dt_start) or 1
            aud_date_start = aud_date_start +' 04:00:00'
            aud_date_end = aud_date_end + ' 23:58:58'
            fot_data = []
            engineer_task_count = 0
            utl_list = []
            fot_list =[]
            for user_id in user_ids:
                domain = [('od_type','=','activities'),('user_id','=',user_id),('od_stage','=','done')]
                domain.extend([('date_start','>=',aud_date_start),('date_start','<=',aud_date_end)]) 
                data_ids =self.env[data_model].search(domain)
                spent_time = 0.0
                fot = sum([dat.od_end_kpi*(100/60.0) for dat in data_ids])/(float(len(data_ids)) or 1.0)
                engineer_task_count += len(data_ids)
                for data in data_ids:
                    spent_time += sum([work.hours for work in data.work_ids])
                utl = spent_time/avl_time
                result.append((0,0,{'user_id':user_id,'available_time':avl_time,'actual_time_spent':spent_time,'utl':spent_time/avl_time}))
                fot_data.append((0,0,{'user_id':user_id,'fot':fot}))
                if utl >=.65:
                    utl =1
                utl_list.append(utl)
                fot_list.append(fot)
            
            utl_score = sum(utl_list)/(float(len(utl_list)) or 1.0)
            fot_score  = sum(fot_list)/(float(len(fot_list)) or 1.0)
            cancelled_activities = self.get_cancelled_activities(self.user_id.id,aud_date_start,aud_date_end,engineer_task_count) 
            escalation_activities = self.get_escalation_activities(aud_date_start,aud_date_end,user_ids)
            
            weight_escalate = escalation_activities.get('weight_escalate',False)
            weight_task_cancel = cancelled_activities.get('weight_task',False)
            print "weight escalate>>>>>>>>>>>>>>>>>>>>>> weight task cancel>>>>>>>>>>>",weight_escalate,weight_task_cancel
            wt_esc = wt_tsk_cncl = wt_utl = wt_fot =0.0
            if weight_escalate and not weight_task_cancel:
                wt_esc= 10+ (10 *(30/70.0))
                wt_tsk_cncl =0.0
                wt_utl = 30+ (30 *(30/70.0))
                wt_fot = 30+ (30 *(30/70.0))
            if not weight_escalate and weight_task_cancel:
                wt_esc= 0.0
                wt_tsk_cncl =30+ (30 *(10/90))
                wt_utl = 30+ (30 *(10/90))
                wt_fot = 30+ (30 *(10/90))
            if not weight_escalate and not weight_task_cancel:
                wt_esc= 0.0
                wt_tsk_cncl =0.0
                wt_utl = 30+ (30 *(40/60))
                wt_fot = 30+ (30 *(40/60))
            if weight_escalate and weight_task_cancel:
                wt_esc= 10
                wt_tsk_cncl =30
                wt_utl = 30
                wt_fot = 30
            tsk_cncl_scr = cancelled_activities.get('score',0.0)
            esc_scr =escalation_activities.get('score',0.0)
            comp_data = []
            comp_data.append((0,0,{'name':'Finished On Time','weight':wt_fot,'score':fot_score,'final_score':(wt_fot/100.0) * fot_score}))
            comp_data.append((0,0,{'name':'Team Utilization','weight':wt_utl,'score':utl_score,'final_score':wt_utl * utl_score}))
            if wt_tsk_cncl:
                comp_data.append((0,0,{'name':'Percentage Of Cancelled Activities','weight':wt_tsk_cncl,'score':tsk_cncl_scr,'final_score':wt_tsk_cncl * tsk_cncl_scr}))
            if wt_esc:
                comp_data.append((0,0,{'name':'Escalation From Activity Owner','weight':wt_esc,'score':esc_scr,'final_score':wt_esc * esc_scr}))
            sample_id.utl_sample_line.unlink()
            sample_id.ttl_fot_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'utl_sample_line':result,'ttl_fot_line':fot_data,'comp_line':comp_data})
    
    def get_available_time(self,aud_date_start):
       
        fromdate = datetime.strptime(aud_date_start, DEFAULT_SERVER_DATE_FORMAT)
        todate = datetime.today()
        daygenerator = (fromdate + timedelta(x + 1) for x in xrange((todate - fromdate).days))
        days =sum(1 for day in daygenerator if day.weekday() not in (4,5)) 
        days +=1
        return days*9
    
    def get_cancelled_activities(self,user_id,aud_date_start,aud_date_end,engineer_task_count):
        task = self.env['project.task']
        domain = [('od_type','=','activities'),('cancel_tl_id','=',user_id),('od_stage','=','cancel_by_tl')]
        domain.extend([('date_start','>=',aud_date_start),('date_start','<=',aud_date_end)]) 
        task_ids  =task.search(domain)
        if task_ids:
            no_of_cancel_act = len(task_ids)
            tolerance = no_of_cancel_act/engineer_task_count
            if tolerance>10:
                return {'score':0.0,'weight_task':True}
            else:
                return {'score':1.0,'weight_task':True}
                
        else:
            return {'weight_task':False,'score':0.0}
    def get_escalation_activities(self,aud_date_start,aud_date_end,user_ids):
        resolved =0
        escalated =0
        for user_id in user_ids:
            domain = [('od_type','=','activities'),('user_id','=',user_id)]
            domain2=[('od_type','=','activities'),('user_id','=',user_id)]
            domain.extend([('date_start','>=',aud_date_start),('date_start','<=',aud_date_end),('od_owner_esc_status','=','resolved')]) 
            resolved_ids =self.env['project.task'].search(domain)
            domain2.extend([('date_start','>=',aud_date_start),('date_start','<=',aud_date_end),('od_owner_esc_status','in',('escalated','not_solved'))])
            resolved +=len(resolved_ids)
            escalated_ids  = self.env['project.task'].search(domain2)
            escalated += len(escalated_ids)
        total_count = resolved + escalated
        if total_count ==0:
            return {'weight_escalate':False,'score':0}
        else:
            return {'weight_escalate':True,'score':resolved/float(total_count)}
        
        
    def create_audit_sample(self,aud_date_start,aud_date_end,audit_temp_id):
        type = audit_temp_id.type
        user_id  = self.user_id and self.user_id.id
        result = []
        sample_id = False
        employee_id = self.id
        dt_start = aud_date_start
        name = self.name + '-' +aud_date_start +' To -'+aud_date_end
        vals = {}
        vals.update({'name':name,'date_start':aud_date_start,'date_end':aud_date_end,
                'aud_temp_id':audit_temp_id.id,'type':type,'employee_id':employee_id})
        
        if type =='post_sales':
            data_model = 'project.task'
            domain = [('od_type','=','activities'),('user_id','=',user_id),('od_stage','=','done')]
            aud_date_start = aud_date_start +' 04:00:00'
            aud_date_end = aud_date_end + ' 23:58:58'
            domain.extend([('date_start','>=',aud_date_start),('date_start','<=',aud_date_end)]) 
            data_ids =self.env[data_model].search(domain)
            for data in data_ids: 
                result.append((0,0,{'task_id':data.id,'score':data.od_total_kpi}))
            vals.update({'post_sale_sample_line':result})
            sample_id =self.env['audit.sample'].create(vals)
        
        
        if type =='ttl':
            eng_ids = self.search([('coach_id','=',employee_id)]) 
            user_ids = [emp.user_id.id for emp in eng_ids] 
            data_model = 'project.task'
            avl_time = self.get_available_time(dt_start) or 1
            aud_date_start = aud_date_start +' 04:00:00'
            aud_date_end = aud_date_end + ' 23:58:58'
            fot_data = []
            engineer_task_count = 0
            utl_list = []
            fot_list =[]
            for user_id in user_ids:
                domain = [('od_type','=','activities'),('user_id','=',user_id),('od_stage','=','done')]
                domain.extend([('date_start','>=',aud_date_start),('date_start','<=',aud_date_end)]) 
                data_ids =self.env[data_model].search(domain)
                spent_time = 0.0
                fot = sum([dat.od_end_kpi*(100/60.0) for dat in data_ids])/(float(len(data_ids)) or 1.0)
                engineer_task_count += len(data_ids)
                for data in data_ids:
                    spent_time += sum([work.hours for work in data.work_ids])
                utl = spent_time/avl_time
                result.append((0,0,{'user_id':user_id,'available_time':avl_time,'actual_time_spent':spent_time,'utl':spent_time/avl_time}))
                fot_data.append((0,0,{'user_id':user_id,'fot':fot}))
                if utl >=.65:
                    utl =1
                utl_list.append(utl)
                fot_list.append(fot)
            
            utl_score = sum(utl_list)/(float(len(utl_list)) or 1.0)
            fot_score  = sum(fot_list)/(float(len(fot_list)) or 1.0)
            cancelled_activities = self.get_cancelled_activities(self.user_id.id,aud_date_start,aud_date_end,engineer_task_count) 
            escalation_activities = self.get_escalation_activities(aud_date_start,aud_date_end,user_ids)
            
            weight_escalate = escalation_activities.get('weight_escalate',False)
            weight_task_cancel = cancelled_activities.get('weight_task',False)
            
            wt_esc = wt_tsk_cncl = wt_utl = wt_fot =0.0
            if weight_escalate and not weight_task_cancel:
                wt_esc= 10+ (10 *(30/70.0))
                wt_tsk_cncl =0.0
                wt_utl = 30+ (30 *(30/70.0))
                wt_fot = 30+ (30 *(30/70.0))
            if not weight_escalate and weight_task_cancel:
                wt_esc= 0.0
                wt_tsk_cncl =30+ (30 *(10/90))
                wt_utl = 30+ (30 *(10/90))
                wt_fot = 30+ (30 *(10/90))
            if not weight_escalate and not weight_task_cancel:
                wt_esc= 0.0
                wt_tsk_cncl =0.0
                wt_utl = 30+ (30 *(40/60))
                wt_fot = 30+ (30 *(40/60))
            if weight_escalate and weight_task_cancel:
                wt_esc= 10
                wt_tsk_cncl =30
                wt_utl = 30
                wt_fot = 30
            tsk_cncl_scr = cancelled_activities.get('score',0.0)
            esc_scr =escalation_activities.get('score',0.0)
            comp_data = []
            comp_data.append((0,0,{'name':'Finished On Time','weight':wt_fot,'score':fot_score,'final_score':(wt_fot/100.0) * fot_score}))
            comp_data.append((0,0,{'name':'Team Utilization','weight':wt_utl,'score':utl_score,'final_score':wt_utl * utl_score}))
            if wt_tsk_cncl:
                comp_data.append((0,0,{'name':'Percentage Of Cancelled Activities','weight':wt_tsk_cncl,'score':tsk_cncl_scr,'final_score':wt_tsk_cncl * tsk_cncl_scr}))
            if wt_esc:
                comp_data.append((0,0,{'name':'Escalation From Activity Owner','weight':wt_esc,'score':esc_scr,'final_score':wt_esc * esc_scr}))
            vals.update({'utl_sample_line':result,'ttl_fot_line':fot_data,'comp_line':comp_data}) 
            sample_id =self.env['audit.sample'].create(vals)
            
            
            #create utlization line
        return sample_id
    
    
    def get_score(self,avg_score,type,ex_num):
            score =avg_score
            if type =='post_sales':
                cert='cert'+ ex_num
                if eval('self.'+cert):
                    score = avg_score * .80
                    cert_st ='cert_status'+ex_num
                    if eval('self.'+cert_st) == 'achieved':
                        score +=20
            if score >100:
                score = 100.0         
            return score
    
    @api.one
    def trial_kpi(self):
        
        audit_temp_id = self.audit_temp_id
        if audit_temp_id:
            type = audit_temp_id.type 
            ex_num = self.get_execution_number()
            ex_num = str(ex_num)
            aud_date_start = eval('self'+'.'+'aud_date_start'+str(ex_num))
            aud_date_end  = eval('self'+'.'+'aud_date_end'+str(ex_num))
            aud_samp = 'audit_sample'+str(ex_num)
            aud_samp_check = eval('self.'+aud_samp)
            scr = 'score'+ex_num
            if aud_samp_check:
                sample_id  = eval('self.'+aud_samp)
                self.update_audit_sample(sample_id,aud_date_start,aud_date_end,audit_temp_id)
                score =  self.get_score(sample_id.avg_score, type, ex_num)
                self.write({scr:score})
            else:
                sample_id =self.create_audit_sample(aud_date_start,aud_date_end,audit_temp_id)
                if sample_id:
                    score =  self.get_score(sample_id.avg_score, type, ex_num)
                    self.write({aud_samp:sample_id.id,scr:score})
     
    
    def audit_set_date(self):
        year='2018'
        day_one =01
        day_end =26
        month_start1 =1
        month_start2 =1
        for i in range(1,13):
            date_start =year+'-'+str(month_start1)+'-'  + str(day_one)
            date_stop = year+'-'+str(month_start2)+'-'  + str(day_end)
            day_one =27
            month_start2+=1
            month_start1= month_start2-1
            sdate ='aud_date_start'+str(i)
            edate ='aud_date_end'+str(i)
            self.write({sdate:date_start,edate:date_stop})
    def audit_set_execution(self):
        today = dt.today()
        month_number = today.month
        day = today.day 
        if day >26:
            month_number +=1
        ext ='execute'+str(month_number)
        self.write({ext:True})
        for i in range(1,13):
            if i != month_number:
                ext = 'execute'+str(i)
                self.write({ext:False})
        
        
        
        
        
