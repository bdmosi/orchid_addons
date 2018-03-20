# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
from openerp.exceptions import Warning
import re
from datetime import date as dt
from datetime import timedelta,datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
class hr_employee(models.Model):
    _inherit ="hr.employee"
    
    
    mgr_score_selection =[(x, x) for x in range(1,11)]
    #audit fileds
    audit_temp_id = fields.Many2one('audit.template',string="Audit Template")
    annual_target = fields.Float(string="Annual Target")
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
    mgr_feedback1 = fields.Boolean(string="Manager Feedback")
    mgr_score1 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl1= fields.Float(string="Utilization")
    
    
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
    mgr_feedback2 = fields.Boolean(string="Manager Feedback")
    mgr_score2 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl2= fields.Float(string="Utilization")
    
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
    mgr_feedback3 = fields.Boolean(string="Manager Feedback")
    mgr_score3 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl3= fields.Float(string="Utilization")
    
    
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
    mgr_feedback4 = fields.Boolean(string="Manager Feedback")
    mgr_score4 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl4= fields.Float(string="Utilization")
    
    
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
    mgr_feedback5 = fields.Boolean(string="Manager Feedback")
    mgr_score5 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl5= fields.Float(string="Utilization")
    
    
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
    mgr_feedback6 = fields.Boolean(string="Manager Feedback")
    mgr_score6 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl6= fields.Float(string="Utilization")
    
    
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
    mgr_feedback7 = fields.Boolean(string="Manager Feedback")
    mgr_score7 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl7= fields.Float(string="Utilization")
    
    
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
    mgr_feedback8 = fields.Boolean(string="Manager Feedback")
    mgr_score8 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl8= fields.Float(string="Utilization")

    
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
    mgr_feedback9 = fields.Boolean(string="Manager Feedback")
    mgr_score9 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl9= fields.Float(string="Utilization")
    
    
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
    mgr_feedback10 = fields.Boolean(string="Manager Feedback")
    mgr_score10 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl10= fields.Float(string="Utilization")

    
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
    mgr_feedback11 = fields.Boolean(string="Manager Feedback")
    mgr_score11 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl11= fields.Float(string="Utilization")
    
    
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
    mgr_feedback12 = fields.Boolean(string="Manager Feedback")
    mgr_score12 = fields.Selection(mgr_score_selection,string="Manager Score")
    utl12= fields.Float(string="Utilization")
    
    commit_total = fields.Float(string="Current Month Commit Total")
    
    def get_product_id_from_param(self,product_param):
        parameter_obj = self.env['ir.config_parameter']
        key =[('key', '=', product_param)]
        product_param_obj = parameter_obj.search(key)
        if not product_param_obj:
            raise Warning(_('Settings Warning!'),_('NoParameter Not defined\nconfig it in System Parameters with %s'%product_param))
        product_id = product_param_obj.od_model_id and product_param_obj.od_model_id.id or False
        return product_id
    
    
    def get_default_product_id(self):
        company_id = self.env.user.company_id.id
        param ='uae_engineer_product'
        if company_id ==6:
            param ='ksa_engineer_product'
        product_id = self.get_product_id_from_param(param)
        return product_id
    
    def get_default_timesheet_journal_id(self):
        company_id = self.env.user.company_id.id
        param ='uae_engineer_timesheet'
        if company_id ==6:
            param ='ksa_engineer_timesheet'
        journal_id = self.get_product_id_from_param(param)
        return journal_id
    
    
    
    
    product_id = fields.Many2one('product.product',string="Product",domain=[('type','=','service')],default=get_default_product_id)
    journal_id = fields.Many2one('account.analytic.journal',string="Analytic Journal",default=get_default_timesheet_journal_id)
    
    
      
    
   
    
    
    
    
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
    
    def get_avg_score(self,score_board):
        avg_score =0.0
        if score_board:
            avg_score =sum(score_board)/float(len(score_board))
        return avg_score
    
    def get_post_sales_vals(self,sample_id,aud_date_start,aud_date_end):
        user_id  = self.user_id and self.user_id.id
        result = []
        avl_time = self.get_available_time(aud_date_start,aud_date_end) or 1
        data_model = 'project.task'
        domain = [('od_type','=','activities'),('user_id','=',user_id),('od_stage','=','done')]
        aud_date_start = aud_date_start +' 04:00:00'
        aud_date_end = aud_date_end + ' 23:58:58'
        domain.extend([('date_start','>=',aud_date_start),('date_start','<=',aud_date_end)]) 
        data_ids =self.env[data_model].search(domain)
       
        spent_time  = sum([dat.od_actual for dat in data_ids])
        utilization = (spent_time/float(avl_time)) *100
        score_board = []
        comp_data =[]
        for data in data_ids: 
            result.append((0,0,{'task_id':data.id,'score':data.od_total_kpi}))
            score_board.append(data.od_total_kpi)
            
        res = self.get_certificate_status()
        wt_cert = wt_task =cert_score =0.0
        if res.get('required'):
            wt_cert =20.0
            wt_task =80
            if res.get('achieved'):
                cert_score =100.0
        else:
            wt_cert =0.0
            wt_task =100
        avg_score =self.get_avg_score(score_board)
        comp_data.append((0,0,{'name':'Activity Integrity','weight':wt_task,'score':avg_score,'final_score':(wt_task/100.0)*avg_score}))
        if wt_cert:
            comp_data.append((0,0,{'name':'Certificate','weight':wt_cert,'score':cert_score,'final_score':(wt_cert/100.0)*cert_score}))
        return result,comp_data,utilization
        
    
    
    
    
    def get_x_days(self,date_start,date_end):
        fromdate = datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT)
        todate = datetime.strptime(date_end, DEFAULT_SERVER_DATE_FORMAT)
        daygenerator = (fromdate + timedelta(x + 1) for x in xrange((todate - fromdate).days))
        days =sum(1 for day in daygenerator)
        days = days+1
        return days  
    def get_available_time(self,aud_date_start,aud_date_end):
       
        fromdate = datetime.strptime(aud_date_start, DEFAULT_SERVER_DATE_FORMAT)
        todate = datetime.today()
        date_end = datetime.strptime(aud_date_end, DEFAULT_SERVER_DATE_FORMAT)
        if todate > date_end:
            todate = date_end
        daygenerator = (fromdate + timedelta(x + 1) for x in xrange((todate - fromdate).days))
        days =sum(1 for day in daygenerator if day.weekday() not in (4,5)) 
        days = days+1
        return days*9
    
    def get_cancelled_activities(self,user_id,aud_date_start,aud_date_end,engineer_task_count):
        task = self.env['project.task']
        domain = [('od_type','=','activities'),('cancel_tl_id','=',user_id),('od_stage','=','cancel_by_tl')]
        domain.extend([('date_start','>=',aud_date_start),('date_start','<=',aud_date_end)]) 
        task_ids  =task.search(domain)
        if task_ids:
            no_of_cancel_act = len(task_ids)
            tolerance =0.0
            if engineer_task_count:
                tolerance = no_of_cancel_act/float(engineer_task_count)
            if tolerance>10:
                return {'score':0.0,'weight_task':True}
            else:
                return {'score':100.0,'weight_task':True}
                
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
        
        
    def get_ttl_vals(self,sample_id,user_id,aud_date_start,aud_date_end,audit_temp_id):
        type = audit_temp_id.type
#         user_id  = self.user_id and self.user_id.id
        employee = self.search([('user_id','=',user_id)],limit=1)
        employee_id = employee.id
        dt_start = aud_date_start
        result = []
        eng_ids = self.search([('coach_id','=',employee_id)]) 
        user_ids = [emp.user_id.id for emp in eng_ids] 
        data_model = 'project.task'
        avl_time = self.get_available_time(dt_start,aud_date_end) or 1
        aud_date_start = aud_date_start +' 04:00:00'
        aud_date_end = aud_date_end + ' 23:58:58'
        fot_data = []
        engineer_task_count = 0
        utl_list = []
        fot_list =[]
        for user in user_ids:
            domain = [('od_type','=','activities'),('user_id','=',user),('od_stage','=','done')]
            domain.extend([('date_start','>=',aud_date_start),('date_start','<=',aud_date_end)]) 
            data_ids =self.env[data_model].search(domain)
            spent_time = sum([dat.od_actual for dat in data_ids])
            fot_board = [dat.od_end_kpi*(100/60.0) for dat in data_ids]
            fot = self.get_avg_score(fot_board)
            engineer_task_count += len(data_ids)
#             for data in data_ids:
#                 spent_time += sum([work.hours for work in data.work_ids])
            utl = spent_time/float(avl_time)
            result.append((0,0,{'user_id':user,'available_time':avl_time,'actual_time_spent':spent_time,'utl':(spent_time/avl_time)*100.0}))
            fot_data.append((0,0,{'user_id':user,'fot':fot}))
            utl  = (utl/0.65)
            utl_list.append(utl)
            fot_list.append(fot)
            
        utl_score =  self.get_avg_score(utl_list)  
        fot_score  = self.get_avg_score(fot_list)   
        cancelled_activities = self.get_cancelled_activities(user_id,aud_date_start,aud_date_end,engineer_task_count) 
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
            wt_tsk_cncl =30+ (30 *(10/90.0))
            wt_utl = 30+ (30 *(10/90.0))
            wt_fot = 30+ (30 *(10/90.0))
        if not weight_escalate and not weight_task_cancel:
            wt_esc= 0.0
            wt_tsk_cncl =0.0
            wt_utl = 30+ (30 *(40/60.0))
            wt_fot = 30+ (30 *(40/60.0))
                
        if weight_escalate and weight_task_cancel:
                
            wt_esc= 10
            wt_tsk_cncl =30
            wt_utl = 30
            wt_fot = 30
        tsk_cncl_scr = cancelled_activities.get('score',0.0)
        esc_scr =escalation_activities.get('score',0.0)
        comp_data = []
        comp_data.append((0,0,{'name':'Finished On Time','weight':wt_fot,'score':fot_score,'final_score':(wt_fot/100.0) * fot_score}))
        comp_data.append((0,0,{'name':'Team Utilization','weight':wt_utl,'score':utl_score*100,'final_score':wt_utl * utl_score}))
        if wt_tsk_cncl:
            comp_data.append((0,0,{'name':'Percentage Of Cancelled Activities','weight':wt_tsk_cncl,'score':tsk_cncl_scr,'final_score':(wt_tsk_cncl/100.0) * tsk_cncl_scr}))
        if wt_esc:
            comp_data.append((0,0,{'name':'Escalation From Activity Owner','weight':wt_esc,'score':esc_scr*100,'final_score':wt_esc * esc_scr})) 
        return result,fot_data,comp_data
    
    
    def get_tech_hoo_comp_line(self,fot_score,utl_score,c_score,c_wt):
        comp_data = []
        wt_fot =.1 
        wt_utl =.1
        wt_cancel =.1 
        exclude_wt =0.0 
        if not c_wt:
            exclude_wt += wt_cancel
            wt_cancel =0.0
        if exclude_wt:
            wt_fot =  wt_fot + .05
            wt_utl=wt_utl + .05
         
        if wt_fot:
            score = fot_score 
            final_score = wt_fot * score
            comp_data.append((0,0,{'name':'Average of Team -Finished On Time','weight':wt_fot*100.0,'final_score':final_score,'score':score}))
        
        if wt_utl:
            score = utl_score 
            final_score = wt_utl * score
            comp_data.append((0,0,{'name':'Average of Team Utilization','weight':wt_utl*100.0,'final_score':final_score,'score':score}))
        if wt_cancel:
            score = c_score 
            final_score = wt_cancel * score
            comp_data.append((0,0,{'name':'Average of Team Percentage Of Cancelled Activities','weight':wt_cancel*100.0,'final_score':final_score,'score':score}))
        return comp_data
    def get_tech_comp_hoo(self,tl_comp_line):
        res =[]
        fot_score_board =[]
        utl_score_board = []
        c_board =[]
        for _,_,val in tl_comp_line:
            if val.get('name','') == 'Finished On Time':
                score = val.get('score')
                fot_score_board.append(score)
            
            if val.get('name','') == 'Team Utilization':
                score = val.get('score')
                utl_score_board.append(score)
            
            if val.get('name','') == 'Percentage Of Cancelled Activities':
                score = val.get('score')
                c_board.append(score)
        c_wt = False
        fot_score = self.get_avg_score(fot_score_board)
        utl_score  = self.get_avg_score(utl_score_board)
        c_score = self.get_avg_score(c_board)
        if c_board:
            c_wt = True
        tech_comp_line= self.get_tech_hoo_comp_line(fot_score, utl_score, c_score, c_wt)
        return tech_comp_line
    
    def get_pmo_score_from_comp(self,pmo_comp_line):
        final_score =0.0
        for _,_,val in pmo_comp_line:
            final_score += val.get('final_score')
        return final_score
    def get_hoo_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        employee = self.search([('user_id','=',user_id)],limit=1)
        employee_id = employee.id
        team_ids = self.search([('parent_id','=',employee_id)]) 
        tl_user_ids = [emp.user_id.id for emp in team_ids if (emp.audit_temp_id and emp.audit_temp_id.type =='ttl')]
        
        
        utl_vals = []
        fot_vals = []
        tl_comp_line = []
        for user in tl_user_ids:
            utl_data,fot_data,ttl_comp = self.get_ttl_vals(sample_id, user, aud_date_start, aud_date_end, audit_temp_id)
            utl_vals += utl_data
            fot_vals += fot_data 
            tl_comp_line += ttl_comp
        
        sd_user_ids = [emp.user_id.id for emp in team_ids if (emp.audit_temp_id and emp.audit_temp_id.type =='sde')]
        team_score = []
        team_vals =[]
        for user in sd_user_ids:
            dum1,dum2,dum3,comp_line = self.get_sde_data(sample_id,user, aud_date_start, aud_date_end, audit_temp_id)
            
            score = self.get_score_from_comp_data(comp_line)
            team_score.append(score)
            team_vals.append((0,0,{'user_id':user,'score':score}))
        tech_comp_line = self.get_tech_comp_hoo(tl_comp_line)
        open_projects,closed_projects,pmo_comp_line = self.get_pmo_dir_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
        pmo_score = self.get_pmo_score_from_comp(pmo_comp_line)
        pmo_comp_line = [(0,0,{'name':'Cash Flow Management','weight':50,'score':pmo_score,'final_score':pmo_score* 0.5})]
        team_avg_score = self.get_avg_score(team_score)
        sde_comp_line = [(0,0,{'name':'Average Of Service Desk Engineer','weight':20,'score':team_avg_score,'final_score':team_avg_score* 0.2})]
        comp_line = tech_comp_line + pmo_comp_line + sde_comp_line
        
        
        return utl_vals,fot_vals,open_projects,closed_projects,team_vals,comp_line
    def get_tech_cons_ps_vals(self,sample_id,aud_date_start,aud_date_end,audit_temp_id):
        type = audit_temp_id.type
        usr_id  = self.user_id and self.user_id.id
        employee_id = self.id
        dt_start = aud_date_start
        result = []
        eng_ids = self.search([('coach_id','=',employee_id)]) 
        user_ids = [emp.user_id.id for emp in eng_ids if (emp.audit_temp_id and emp.audit_temp_id.type =='post_sales')] + [usr_id]
        data_model = 'project.task'
        avl_time = self.get_available_time(dt_start,aud_date_end) or 1
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
            spent_time = sum([dat.od_actual for dat in data_ids])
            fot_board = [dat.od_end_kpi*(100/60.0) for dat in data_ids]
            fot = self.get_avg_score(fot_board)
            engineer_task_count += len(data_ids)
#             for data in data_ids:
#                 spent_time += sum([work.hours for work in data.work_ids])
            utl = spent_time/float(avl_time)
            if user_id !=usr_id:
                result.append((0,0,{'user_id':user_id,'available_time':avl_time,'actual_time_spent':spent_time,'utl':(spent_time/avl_time)*100.0}))
                utl  = (utl/0.65)
                utl_list.append(utl)
            if data_ids:
                fot_data.append((0,0,{'user_id':user_id,'fot':fot}))
                fot_list.append(fot)
            
        utl_score =  self.get_avg_score(utl_list)  
        fot_score  = self.get_avg_score(fot_list)   
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
            wt_tsk_cncl =30+ (30 *(10/90.0))
            wt_utl = 30+ (30 *(10/90.0))
            wt_fot = 30+ (30 *(10/90.0))
        if not weight_escalate and not weight_task_cancel:
            wt_esc= 0.0
            wt_tsk_cncl =0.0
            wt_utl = 30+ (30 *(40/60.0))
            wt_fot = 30+ (30 *(40/60.0))
                
        if weight_escalate and weight_task_cancel:
                
            wt_esc= 10
            wt_tsk_cncl =30
            wt_utl = 30
            wt_fot = 30
        tsk_cncl_scr = cancelled_activities.get('score',0.0)
        esc_scr =escalation_activities.get('score',0.0)
        comp_data = []
        comp_data.append((0,0,{'name':'Finished On Time','weight':wt_fot,'score':fot_score,'final_score':(wt_fot/100.0) * fot_score}))
        comp_data.append((0,0,{'name':'Team Utilization','weight':wt_utl,'score':utl_score*100,'final_score':wt_utl * utl_score}))
        if wt_tsk_cncl:
            comp_data.append((0,0,{'name':'Percentage Of Cancelled Activities','weight':wt_tsk_cncl,'score':tsk_cncl_scr,'final_score':(wt_tsk_cncl/100.0) * tsk_cncl_scr}))
        if wt_esc:
            comp_data.append((0,0,{'name':'Escalation From Activity Owner','weight':wt_esc,'score':esc_scr*100,'final_score':wt_esc * esc_scr})) 
        return result,fot_data,comp_data
    
    
    
    def get_presale_data(self,user_id, aud_date_start, aud_date_end, audit_temp_id):
        
        result = []
        data_model = 'crm.lead'
        domain = [('stage_id','!=',8),('od_responsible_id','=',user_id)]
        aud_date_start = aud_date_start 
        aud_date_end = aud_date_end 
        domain.extend([('od_req_on_7','>=',aud_date_start),('od_req_on_7','<=',aud_date_end)]) 
        data_ids =self.env[data_model].search(domain)
        score_boards = []
        comp_data =[]
        for data in data_ids:
            score=0.0
            if data.finished_on_7 <= data.od_req_on_7:
                score = 100.0
            score_boards.append(score) 
            result.append((0,0,{'opp_id':data.id,'score':score,'user_id':user_id}))
        avg_score = self.get_avg_score(score_boards)
        return result,avg_score
    def get_presale_vals(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        user_id  = self.user_id and self.user_id.id
        result = []
        data_model = 'crm.lead'
        domain = [('stage_id','!=',8),('od_responsible_id','=',user_id)]
        aud_date_start = aud_date_start 
        aud_date_end = aud_date_end 
        domain.extend([('od_req_on_7','>=',aud_date_start),('od_req_on_7','<=',aud_date_end)]) 
        data_ids =self.env[data_model].search(domain)
        score_boards = []
        comp_data =[]
        for data in data_ids:
            score=0.0
            if data.finished_on_7 <= data.od_req_on_7:
                score = 100.0
            score_boards.append(score) 
            result.append((0,0,{'opp_id':data.id,'score':score,'user_id':user_id}))
        avg_score = self.get_avg_score(score_boards)
        res = self.get_certificate_status()
        wt_cert = wt_opp =cert_score =0.0
        if res.get('required'):
            wt_cert =20.0
            wt_opp =80
            if res.get('achieved'):
                cert_score =100.0
        else:
            wt_cert =0.0
            wt_opp =100
        comp_data.append((0,0,{'name':'Productivity','weight':wt_opp,'score':avg_score,'final_score':(wt_opp/100.0)*avg_score}))
        if wt_cert:
            comp_data.append((0,0,{'name':'Certificate','weight':wt_cert,'score':cert_score,'final_score':(wt_cert/100.0)*cert_score}))
        return result,comp_data
    
    def get_presale_mgr_vals_tc(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        user_id  = self.user_id and self.user_id.id
        employee_id = self.id
        team_ids = self.search([('coach_id','=',employee_id)]) 
        user_ids = [emp.user_id.id for emp in team_ids if (emp.audit_temp_id and emp.audit_temp_id.type=='pre_sales')]
        result = []
        team_score =[]
        team_vals =[] 
        for uid in user_ids:
            data,avg_score = self.get_presale_data(uid, aud_date_start, aud_date_end, audit_temp_id)
            team_score.append(avg_score)
            team_vals.append((0,0,{'user_id':uid,'score':avg_score}))
            result.extend(data)
            
        team_avg_score =  self.get_avg_score(team_score)  
        comp_data =[(0,0,{'name':'Productivity','weight':100.0,'score':team_avg_score,'final_score':team_avg_score})]
        return result,team_vals,comp_data
    
    def get_presale_mgr_vals(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        user_id  = self.user_id and self.user_id.id
        employee_id = self.id
        team_ids = self.search([('coach_id','=',employee_id)]) 
        user_ids = [emp.user_id.id for emp in team_ids] + [user_id]
        result = []
        team_score =[]
        team_vals =[] 
        for uid in user_ids:
            data,avg_score = self.get_presale_data(uid, aud_date_start, aud_date_end, audit_temp_id)
            team_score.append(avg_score)
            team_vals.append((0,0,{'user_id':uid,'score':avg_score}))
            result.extend(data)
            
        team_avg_score =  self.get_avg_score(team_score)  
        comp_data =[(0,0,{'name':'Productivity','weight':100,'score':team_avg_score,'final_score':team_avg_score})]
        return result,team_vals,comp_data
    def get_sales_commit_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        
        total_gp = 0.0
        
        result =[]
        domain = [('sales_acc_manager','=',user_id),('status','=','active')]
        domain.extend([('op_expected_booking','>=',aud_date_start),('op_expected_booking','<=',aud_date_end)])
        domain1 = domain + [('state','not in',('approved','done','cancel','modify','change','analytic_change','draft','design_ready','submitted'))]
        domain2 = domain + [('state','in',('draft','design_ready','submitted'))]
        
        sheet_ids =self.env['od.cost.sheet'].search(domain1)
        
        for sheet in sheet_ids:
            gp =sheet.total_gp
            result.append((0,0,{'cost_sheet_id':sheet.id,'gp':gp}))
            total_gp += gp
        sheet_ids =self.env['od.cost.sheet'].search(domain2)
        for sheet in sheet_ids:
            stage_id = sheet.op_stage_id and sheet.op_stage_id.id 
            if stage_id in (5,12):
                gp = sheet.total_gp
                result.append((0,0,{'cost_sheet_id':sheet.id,'gp':gp,'user_id':user_id}))
                total_gp +=gp
        return result,total_gp
    def get_sales_achieved_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        
        result =[]
        total_gp = 0.0
        domain = [('sales_acc_manager','=',user_id),('status','=','active')]
        domain.extend([('op_expected_booking','>=',aud_date_start),('op_expected_booking','<=',aud_date_end)])
        domain1 = domain + [('state','in',('approved','done','modify','change','analytic_change'))]
        sheet_ids =self.env['od.cost.sheet'].search(domain1)
        for sheet in sheet_ids:
            gp = sheet.total_gp
            result.append((0,0,{'cost_sheet_id':sheet.id,'gp':sheet.total_gp,'user_id':user_id}))
            total_gp +=gp
        return result,total_gp
    def get_sales_acc_mgr_component(self,commit_total,achieved_total):
        target = self.annual_target/12.0
        result =0.0
        exclude_wt = 0.0
        comp_data =[]
        if target:
            if achieved_total >= commit_total:
                result = commit_total/target
                if result >3.0:
                    result =3
            elif achieved_total < commit_total:
                result = achieved_total/target 
                if result > 1.5:
                    result =1.5
        mgr_score = self.get_mgr_feedback()
        cert = self.get_certificate_status()
        cert_ach = cert.get('achieved',False)
        cert_req = cert.get('required',False)
        if not mgr_score:
            exclude_wt += 10
        if not cert_req:
            exclude_wt += 10
        
        wt_cmt = 80.0
        wt_cert =10.0
        wt_mgr =10.0
        if exclude_wt:
            wt_cmt =  wt_cmt + (wt_cmt*exclude_wt)/float(100-exclude_wt)
            wt_cert =  wt_cert + (wt_cert*exclude_wt)/float(100-exclude_wt)
            wt_mgr =  wt_mgr + (wt_mgr*exclude_wt)/float(100-exclude_wt)
        
        comp_data.append((0,0,
                              {'name':'Commitment Performance',
                               'weight':wt_cmt,
                               'score':result*100,
                               'final_score':wt_cmt *result}
                              ))
            
        if cert_req:
            cert_score  =0.0
            if cert_ach:
                cert_score = 100
            comp_data.append((0,0,
                              {'name':'Certificate',
                               'weight':wt_cert,
                               'score':cert_score,
                               'final_score':(wt_cert/100.0)*cert_score}
                              ))
        if mgr_score:
            comp_data.append((0,0,
                              {'name':'Direct Manager Feedback',
                               'weight':wt_mgr,
                               'score':mgr_score*10,
                               'final_score':(wt_mgr/10.0)*mgr_score}
                              ))
        
        return comp_data,target
    
    def get_sales_acc_mgr_component_sm(self,emp_id,commit_total,achieved_total):
        emp = self.browse(emp_id)
        target = emp.annual_target/12.0
        result =0.0
        exclude_wt = 0.0
        comp_data =[]
        if target:
            if achieved_total >= commit_total:
                result = commit_total/target
                if result >3.0:
                    result =3
            elif achieved_total < commit_total:
                result = achieved_total/target 
                if result > 1.5:
                    result =1.5
        mgr_score = emp.get_mgr_feedback()
        cert = emp.get_certificate_status()
        cert_ach = cert.get('achieved',False)
        cert_req = cert.get('required',False)
        if not mgr_score:
            exclude_wt += 10
        if not cert_req:
            exclude_wt += 10
        
        wt_cmt = 80.0
        wt_cert =10.0
        wt_mgr =10.0
        if exclude_wt:
            wt_cmt =  wt_cmt + (wt_cmt*exclude_wt)/float(100-exclude_wt)
            wt_cert =  wt_cert + (wt_cert*exclude_wt)/float(100-exclude_wt)
            wt_mgr =  wt_mgr + (wt_mgr*exclude_wt)/float(100-exclude_wt)
        
        comp_data.append((0,0,
                              {'name':'Commitment Performance',
                               'weight':wt_cmt,
                               'score':result*100,
                               'final_score':wt_cmt *result}
                              ))
            
        if cert_req:
            cert_score  =0.0
            if cert_ach:
                cert_score = 100
            comp_data.append((0,0,
                              {'name':'Certificate',
                               'weight':wt_cert,
                               'score':cert_score,
                               'final_score':(wt_cert/100.0)*cert_score}
                              ))
        if mgr_score:
            comp_data.append((0,0,
                              {'name':'Direct Manager Feedback',
                               'weight':wt_mgr,
                               'score':mgr_score*10,
                               'final_score':(wt_mgr/10.0)*mgr_score}
                              ))
        
        return comp_data,target
    
    def get_sm_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        type = audit_temp_id.type
        employee_id = self.id
        sam_ids = self.search([('parent_id','=',employee_id)]) 
        emp_ids = [emp for emp in sam_ids if (emp.audit_temp_id and emp.audit_temp_id.type =='sales_acc_mgr')]
        ach_data =[]
        team_comp_data = []
        score_board =[]
        for emp in emp_ids:
            commit_total = emp.commit_total 
            usr_id = emp.user_id and emp.user_id.id or False
            ach_val,ach_total = self.get_sales_achieved_data(sample_id, usr_id, aud_date_start, aud_date_end, audit_temp_id)
            team_comp_val,target = self.get_sales_acc_mgr_component_sm(emp.id,commit_total, ach_total)
            ach_data.extend(ach_val)
            score = self.get_score_from_comp_data(team_comp_val)
            team_comp_data.append((0,0,{'user_id':usr_id,'score':score}))
            score_board.append(score)
        avg_score = self.get_avg_score(score_board)
        wt =1.0
        score =avg_score 
        final_score = wt * avg_score
        comp_line = [(0,0, {'name':'Average Team Performance','weight':wt*100.0,'score':score,'final_score':final_score})]
        return ach_data,team_comp_data,comp_line
        
    
    def get_sdm_component(self,avg_day_score,avg_hd_score):
        comp_data = []
        wt_day = .2 
        wt_hd = .8
        
        print "average day score>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>avg hd_score",avg_day_score,avg_hd_score
        score = avg_day_score
        final_score = score * wt_day
        comp_data.append((0,0,{'name':'Average Of Team Performance - 5 Day Processing','score':score,'weight':wt_day*100.0,'final_score':final_score}))
       
        score = avg_hd_score
        final_score = score * wt_hd
        comp_data.append((0,0,{'name':'Average Of Team Performance -Help Desk Issue Management','score':score,'weight':wt_hd*100.0,'final_score':final_score}))
        return comp_data
    
          
    
    def get_sdm_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        type = audit_temp_id.type
        employee_id = self.id
        team_ids = self.search([('parent_id','=',employee_id)]) 
        user_ids = [emp.user_id.id for emp in team_ids if (emp.audit_temp_id and emp.audit_temp_id.type =='sde')]
        print "user ids>>>>>>>>>>>>>>>>>>>>>>>>>>",user_ids
        day_score_board = []
        team_day_score_val = []
        
        team_hd_vals  =[]
        team_hd_score_board =[]
        for user in user_ids:
            dum1,dum2,dum3,comp_line = self.get_sde_data(sample_id,user, aud_date_start, aud_date_end, audit_temp_id)
            print "comp line>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",dum1,dum2
            for _,_,val in comp_line:
                print "valsssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss sdm>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ",val
                if val.get('name','') == '5 Day Processing Score':
                    score =val.get('score',0.0)
                    team_day_score_val.append((0,0,{'user_id':user,'score':score}))
                    day_score_board.append(score)
                    
                if val.get('name','') == 'Help Desk Issue Management':
                    score =val.get('score',0.0)
                    team_hd_vals.append((0,0,{'user_id':user,'score':score}))
                    team_hd_score_board.append(score)
        print "day score vals>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",team_day_score_val,day_score_board
        avg_day_score = self.get_avg_score(day_score_board)    
        avg_hd_score = self.get_avg_score(team_hd_score_board) 
        comp_line = self.get_sdm_component(avg_day_score,avg_hd_score)   
        return team_day_score_val,team_hd_vals,comp_line
    
    
    
    def check_date_in_audit(self,aud_date_start, aud_date_end,date):
        res = False
        if aud_date_start <= date <= aud_date_end:
            res = True
        if date <= aud_date_start:
            res = True
        return res
#     def get_pm_invoice_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):        
#         user_id  = self.user_id and self.user_id.id
#         analytic_pool = self.env['account.analytic.account']
#         analytic_ids = analytic_pool.search([('od_owner_id','=',user_id),('state','not in',('close','cancelled'))])
#         project_closed_on_audit = analytic_pool.search([('od_owner_id','=',user_id),('state','=','close'),('date','>=',aud_date_start),('date','<=',aud_date_end)])
#         
#         pr_ids  = [a.id for a in analytic_ids] 
#         closed_ids =[y.id for y in project_closed_on_audit]
#         project_ids = pr_ids + closed_ids 
#         project_ids = list(set(project_ids))
#         planned_date_vals = []
#         customer_invoice_vals = []
#         pl_amounts = []
#         inv_amounts = []
#         print "project ids>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",project_ids
#         if project_ids:
#             print "inside the looooooooooooooooooooooooooooooop"
#             for proj in analytic_pool.browse(project_ids):
#                 pl_amount =0.0
#                 type = proj.od_type_of_project 
# #                 if type == 'amc':
# #                     for line in proj.od_amc_invoice_schedule_line:
# #                         date = line.date 
# #                         check = self.check_date_in_audit(aud_date_start, aud_date_end, date)
# #                         if check:
# #                             pl_amount += line.amount
# #                             pl_amounts.append(line.amount)
# #                     if pl_amount:
# #                         planned_date_vals.append((0,0,{'analytic_id':proj.id,'amount':pl_amount}))
# #                 if type  == 'o_m':
# #                     for line in proj.od_om_invoice_schedule_line:
# #                         date = line.date 
# #                         check = self.check_date_in_audit(aud_date_start, aud_date_end, date)
# #                         if check:
# #                             pl_amount += line.amount
# #                             pl_amounts.append(line.amount)
# #                     if pl_amount:
# #                         planned_date_vals.append((0,0,{'analytic_id':proj.id,'amount':pl_amount}))
#                 if type not in ('credit','amc','o_m'):
#                     for line in proj.od_project_invoice_schedule_line:
#                         date = line.date 
#                         check = self.check_date_in_audit(aud_date_start, aud_date_end, date)
#                         if check:
#                             pl_amount += line.amount
#                             pl_amounts.append(line.amount)
#                     if pl_amount:
#                         planned_date_vals.append((0,0,{'analytic_id':proj.id,'amount':pl_amount}))
#                 
#                 invoice_ids = self.env['account.invoice'].search([('od_analytic_account','=',proj.id),('state','in',('open','paid'))])
#                 for inv in invoice_ids:
#                     customer_invoice_vals.append((0,0,{'invoice_id':inv.id,'analytic_id':proj.id,'amount':inv.amount_total}))
#                     inv_amounts.append(inv.amount_total)
#         return planned_date_vals,customer_invoice_vals,sum(pl_amounts),sum(inv_amounts)
            
#     def get_pm_component(self,planned_amount,invoice_amount):
#         comp_data  =[]
#         wt_inv =30
#         if planned_amount:
#             inv_scr = (invoice_amount/float(planned_amount))*100
#             comp_data.append((0,0,{'name':'Invoice Schedule','weight':wt_inv,'final_score':(wt_inv/100.0)*inv_scr,'score':inv_scr}))
#         return comp_data
    
    
    def get_pm_component(self,day_weight_scr,cc_weight_scr,inv_weight_scr,comp_weight_scr,sc_weight_scr,day_flag,cost_flag,inv_flag,comp_flag,sc_flag):
        comp_data =[]
        day_wt  =.1
        cc_wt = .2
        inv_wt =.3
        comp_wt =.1
        sc_wt = .3
        exclude_wt = 0.0
        if not day_flag:
            exclude_wt += day_wt
            day_wt =0.0 
        if not cost_flag:
            exclude_wt += cc_wt
            cc_wt =0.0
        if not inv_flag:
            exclude_wt += inv_wt
            inv_wt =0.0
        if not comp_flag:
            exclude_wt += comp_wt 
            comp_wt =0.0
        if not sc_flag:
            exclude_wt += sc_wt
            sc_wt =0.0
        if exclude_wt == 1.0:
            return comp_data
        if exclude_wt:
            day_wt =  day_wt + (day_wt*exclude_wt)/float(1.0-exclude_wt)
            cc_wt =  cc_wt + (cc_wt*exclude_wt)/float(1.0-exclude_wt)
            inv_wt =  inv_wt + (inv_wt*exclude_wt)/float(1.0-exclude_wt)
            comp_wt =  comp_wt + (comp_wt*exclude_wt)/float(1.0-exclude_wt)
            sc_wt = sc_wt + (sc_wt*exclude_wt)/float(1.0-exclude_wt)
        if day_wt:
            score = (day_weight_scr/10.0) *100.0
            final_score = day_wt * score
            comp_data.append((0,0,{'name':'5 Day Processing Score','weight':day_wt*100.0,'final_score':final_score,'score':score}))
        
        if cc_wt:
            score = (cc_weight_scr/20.0) *100.0
            final_score = cc_wt * score
            comp_data.append((0,0,{'name':'Cost Control','weight':cc_wt*100.0,'final_score':final_score,'score':score}))
            
        if inv_wt:
            score = (inv_weight_scr/30.0) *100.0
            final_score = inv_wt * score
            comp_data.append((0,0,{'name':'Invoice Schedule','weight':inv_wt*100,'final_score':final_score,'score':score}))
            
        if comp_wt:
            score = (comp_weight_scr/10.0) *100.0
            final_score = comp_wt * score
            comp_data.append((0,0,{'name':'Compliance Provided By PMO','weight':comp_wt*100.0,'final_score':final_score,'score':score}))
         
        if sc_wt:
            score = (sc_weight_scr/30.0) *100.0
            final_score = sc_wt * score
            comp_data.append((0,0,{'name':'Schedule Control','weight':sc_wt*100.0,'final_score':final_score,'score':score}))
            
                   
        return comp_data
    
    def get_sde_component(self,day_weight_scr,comp_weight_scr,hd_score,cert_score,day_flag,comp_flag,hd_flag,cert_flag):
        comp_data =[]
        day_wt  =.2
        hd_wt = .6
        cert_wt =.1
        comp_wt =.1
        
        exclude_wt = 0.0
        if not day_flag:
            exclude_wt += day_wt
            day_wt =0.0 
        if not hd_flag:
            exclude_wt += hd_wt
            hd_wt =0.0
        if not cert_flag:
            exclude_wt += cert_wt
            cert_wt =0.0
        if not comp_flag:
            exclude_wt += comp_wt 
            comp_wt =0.0
       
        if exclude_wt == 1.0:
            return comp_data
        if exclude_wt:
            day_wt =  day_wt + (day_wt*exclude_wt)/float(1.0-exclude_wt)
            comp_wt =  comp_wt + (comp_wt*exclude_wt)/float(1.0-exclude_wt)
            hd_wt = hd_wt + (hd_wt*exclude_wt)/float(1.0-exclude_wt)
            cert_wt =  cert_wt + (cert_wt*exclude_wt)/float(1.0-exclude_wt)
        if day_wt:
            score = (day_weight_scr/10.0) *100.0
            final_score = day_wt * score
            comp_data.append((0,0,{'name':'5 Day Processing Score','weight':day_wt*100.0,'final_score':final_score,'score':score}))
        
        if comp_wt:
            score = (comp_weight_scr/10.0) *100.0
            final_score = comp_wt * score
            comp_data.append((0,0,{'name':'Compliance Provided By PMO','weight':comp_wt*100.0,'final_score':final_score,'score':score}))
         
        if hd_wt:
            score = hd_score 
            final_score = hd_wt * score
            comp_data.append((0,0,{'name':'Help Desk Issue Management','weight':hd_wt*100.0,'final_score':final_score,'score':score}))
        
        if cert_wt:
            score = cert_score
            final_score = cert_wt * score
            comp_data.append((0,0,{'name':'Certificate','weight':cert_wt*100.0,'final_score':final_score,'score':score}))
            
                   
        return comp_data
        
    
    def check_inv_sch_dates(self,inv_sch_dates,aud_date_start,aud_date_end):
        for date in inv_sch_dates:
            if date <=aud_date_end:
                return True
        return False
    def get_inv_sch_score(self,proj,aud_date_start,aud_date_end):
        project_start_date = proj.od_project_start 
        score_board = []
        check = False
        for line in proj.od_project_invoice_schedule_line:
            planned_date = line.date
            pl_dt = self.get_x_days(project_start_date, planned_date)
            today = str(dt.today())
            td_dt =self.get_x_days(project_start_date, today)
            if td_dt>=pl_dt:
                invoice = line.invoice_id
                planned_amount = line.amount
                invoice_amount = line.invoice_amount
                if planned_amount < invoice_amount:
                    score =0.0
                    check = True 
                    score_board.append(score)
                    continue
                if invoice and invoice.state in ('open','paid','accept'):
                    cust_date = invoice.cust_date 
                    if aud_date_start<=cust_date <= aud_date_end:
                        check = True
                        score = 0.0
                        if cust_date <= planned_date:
                            score = 30.0
                        score_board.append(score)
        avg_score = self.get_avg_score(score_board)
        return check,avg_score
                        
                
        
    
    def get_pm_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        
        analytic_pool = self.env['account.analytic.account']
        analytic_ids = analytic_pool.search([('od_project_owner_id','=',user_id),('od_type_of_project','not in',('amc','o_m','credit')),('state','not in',('close','cancelled'))])
        project_closed_on_audit = analytic_pool.search([('od_project_owner_id','=',user_id),('od_type_of_project','not in',('amc','o_m','credit')),('state','=','close'),('date','>=',aud_date_start),('date','<=',aud_date_end)])
        sample_project_ids = analytic_ids + project_closed_on_audit
        
        day_score_vals  =[]
#         total_sale_value = sum([a.od_project_sale for a in sample_project_ids])
#         max_day_sore =aud_date_endaud_date_endaud_date_end 20 * len(sample_project_ids)
        
        
        cost_control_vals = []
#         total_gp_value = sum([a.od_amended_profit for a in sample_project_ids])
#         max_cc_sore = 30 * len(sample_project_ids)
        
        invoice_schedule_vals =[] 
        compliance_vals =[]
        schedule_control_vals =[]
        schedule_control_vals_main =[]
        day_weight =[]
        cc_weight =[]
        inv_weight =[]
        comp_weight =[]
        sc_weight =[]
        tot_sale_day =0.0
        tot_gp =0.0
        sch_gp =0.0
        tot_sal_inv =0.0
        tot_sal_comp =0.0
        day_score_main = []
        cost_control_val_main =[]
        invoice_schedule_main =[]
        compliance_vals_main =[]
        for proj in sample_project_ids:
            processed_date = proj.od_cost_sheet_id and proj.od_cost_sheet_id.processed_date 
            if processed_date and aud_date_start <= processed_date <= aud_date_end:
                sale_val = proj.od_project_sale
                tot_sale_day += sale_val
                dayscore = proj.day_process_score
                day_score_vals.append({'analytic_id':proj.id,'sale_value':sale_val,'score':dayscore,'cost_sheet_id':proj.od_cost_sheet_id.id,'form_wt':10.0})
            #cost control score
            if proj.state == 'close':
                gp_value = proj.od_amended_profit 
                tot_gp += gp_value
                cost_control_score = proj.cost_control_score 
                cost_control_vals.append({'analytic_id':proj.id,'gp_value':gp_value,'score':cost_control_score,'form_wt':20.0})
            #invoice Schedule Score
#             inv_sch_dates = [a.date for a in proj.od_project_invoice_schedule_line]
#             check = self.check_inv_sch_dates(inv_sch_dates,aud_date_start,aud_date_end)
            check2,inv_score = self.get_inv_sch_score(proj,aud_date_start,aud_date_end)
            if check2:
                invoice_sc_score = inv_score
                sale_val = proj.od_project_sale
                tot_sal_inv  += sale_val
                invoice_schedule_vals.append({'analytic_id':proj.id,'sale_value':sale_val,'score':invoice_sc_score,'form_wt':30.0})
            if proj.start_project_comp:
                compliance_score = proj.compliance_score
                sale_val = proj.od_project_sale
                tot_sal_comp  += sale_val 
                compliance_vals.append({'analytic_id':proj.id,'sale_value':sale_val,'score':compliance_score,'form_wt':10.0})
            if proj.od_project_status == 'close':
                project_planned_end = proj.od_project_end 
                closed_date = proj.od_project_closing 
                if closed_date <= project_planned_end:
                    sc_scr =30.0
                    gp_value = proj.od_amended_profit 
                    sch_gp += gp_value
                    schedule_control_vals.append({'analytic_id':proj.id,'gp_value':gp_value,'score':sc_scr,'form_wt':30.0})
                else:
                    sc_scr =0.0
                    gp_value = proj.od_amended_profit 
                    sch_gp += gp_value
                    schedule_control_vals.append({'analytic_id':proj.id,'gp_value':gp_value,'score':sc_scr,'form_wt':30.0})
                    
        max_day_sore = 10 * len(day_score_vals)
        for data in day_score_vals:
            sal_val_percent =0.0
            sale_value  = data.get('sale_value')
            if tot_sale_day:
                sal_val_percent = sale_value/float(tot_sale_day)
            dayscore = data.get('score')
            weight_day = max_day_sore * sal_val_percent * (dayscore/10.0)
            data['sale_value_percent'] = sal_val_percent *100.0
            data['weight'] = weight_day
            day_weight.append(weight_day)
            day_score_main.append((0,0,data))
        max_cc_sore = 20 * len(cost_control_vals)
        for data in cost_control_vals:
            gp_val_percent =0.0
            gp_value = data.get('gp_value')
            if tot_gp:
                gp_val_percent = gp_value/float(tot_gp)
            score = data.get('score')
            weight_cc = max_cc_sore * gp_val_percent * (score/20.0)
            data['weight'] = weight_cc
            data['gp_value_percent'] = gp_val_percent *100.0
            cc_weight.append(weight_cc)
            cost_control_val_main.append((0,0,data))
        
        
        max_sc_sore = 30 * len(schedule_control_vals)
        for data in schedule_control_vals:
            gp_val_percent =0.0
            gp_value = data.get('gp_value')
            if sch_gp:
                gp_val_percent = gp_value/float(sch_gp)
            score = data.get('score')
            weight_sc = max_sc_sore * gp_val_percent * (score/30.0)
            data['weight'] = weight_sc
            data['gp_value_percent'] = gp_val_percent *100.0
            sc_weight.append(weight_sc)
            schedule_control_vals_main.append((0,0,data))
        
        max_inv_scr = 30 * len(invoice_schedule_vals)
        for data in invoice_schedule_vals:
            sal_val_percent =0.0
            sale_value  = data.get('sale_value')
            if tot_sal_inv:
                sal_val_percent = sale_value/float(tot_sal_inv)
            score = data.get('score')
            weight_inv = max_inv_scr * sal_val_percent * (score/30.0)
            data['sale_value_percent'] = sal_val_percent *100.0
            data['weight'] = weight_inv
            inv_weight.append(weight_inv)
            invoice_schedule_main.append((0,0,data))
        
        max_comp_scr = 10 * len(compliance_vals)
        for data in compliance_vals:
            sal_val_percent =0.0
            sale_value  = data.get('sale_value')
            if tot_sal_comp:
                sal_val_percent = sale_value/float(tot_sal_comp)
            score = data.get('score')
            weight_comp = max_comp_scr * sal_val_percent * (score/10.0)
            data['sale_value_percent'] = sal_val_percent *100.0
            data['weight'] = weight_comp
            comp_weight.append(weight_comp)
            compliance_vals_main.append((0,0,data))
        
            
        day_weight_scr = self.get_avg_score(day_weight)
        cc_weight_scr = self.get_avg_score(cc_weight)
        inv_weight_scr = self.get_avg_score(inv_weight)
        comp_weight_scr = self.get_avg_score(comp_weight )
        sc_weight_scr = self.get_avg_score(sc_weight)
        day_flag = cost_flag = inv_flag= comp_flag= sc_flag=False 
        print "day score main>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",day_score_main
        if day_score_main:
            day_flag =True 
        if cost_control_val_main:
            cost_flag = True
        if invoice_schedule_main:
            inv_flag = True 
        if compliance_vals_main:
            comp_flag = True
        if schedule_control_vals_main:
            sc_flag = True
        comp_line = self.get_pm_component(day_weight_scr,cc_weight_scr,inv_weight_scr,comp_weight_scr,sc_weight_scr,day_flag,cost_flag,inv_flag,comp_flag,sc_flag)
        
        
            
        return day_score_main,cost_control_val_main,invoice_schedule_main,compliance_vals_main,schedule_control_vals_main,comp_line
    
    
    
    def get_hd_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        hd_pool = self.env['crm.helpdesk']
        domain  = [('user_id','=',user_id),('categ_id','in',(16,17))]
        domain.extend([('date_deadline','>=',aud_date_start),('date_deadline','<=',aud_date_end)])
        hd_data = hd_pool.search(domain)
        hd_vals =[]
        score_board =[]
        for hd in hd_data:
            score =hd.od_hd_kpi
            hd_vals.append((0,0,{'hd_id':hd.id,'score':score}))
            score_board.append(score)
        hd_score = self.get_avg_score(score_board)
        print "hd score>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",hd_score
        return hd_vals,hd_score
            
    
    def get_sde_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        analytic_pool = self.env['account.analytic.account']
        analytic_ids = analytic_pool.search([('od_amc_owner_id','=',user_id),('od_type_of_project','=','amc'),('state','not in',('close','cancelled'))])
        project_closed_on_audit = analytic_pool.search([('od_amc_owner_id','=',user_id),('od_type_of_project','=','amc'),('state','=','close'),('date','>=',aud_date_start),('date','<=',aud_date_end)])
        sample_project_ids = analytic_ids + project_closed_on_audit
        day_score_vals  =[]
        day_weight =[]
        tot_sale_day =0.0
        day_score_main = []
        compliance_vals =[]
        comp_weight =[]
        tot_sal_comp =0.0
        compliance_vals_main =[]
        
        for proj in sample_project_ids:
            processed_date = proj.od_cost_sheet_id and proj.od_cost_sheet_id.processed_date
            owner_id = proj.od_cost_sheet_id and proj.od_cost_sheet_id.reviewed_id and  proj.od_cost_sheet_id.reviewed_id.id or False 
            if user_id == owner_id:
                if processed_date and aud_date_start <= processed_date <= aud_date_end:
                    sale_val = proj.od_amc_sale
                    tot_sale_day += sale_val
                    dayscore = proj.day_process_score
                    day_score_vals.append({'analytic_id':proj.id,'sale_value':sale_val,'score':dayscore,'cost_sheet_id':proj.od_cost_sheet_id.id,'form_wt':20.0})
            
            if proj.start_amc_comp:
                compliance_score = proj.compliance_score
                sale_val = proj.od_amc_sale
                tot_sal_comp  += sale_val 
                compliance_vals.append({'analytic_id':proj.id,'sale_value':sale_val,'score':compliance_score,'form_wt':10.0})
        
        max_day_sore = 10.0 * len(day_score_vals)
        for data in day_score_vals:
            sal_val_percent =0.0
            sale_value  = data.get('sale_value')
            if tot_sale_day:
                sal_val_percent = sale_value/float(tot_sale_day)
            dayscore = data.get('score')
            weight_day = max_day_sore * sal_val_percent * (dayscore/10.0)
            data['sale_value_percent'] = sal_val_percent *100.0
            data['weight'] = weight_day
            day_weight.append(weight_day)
            day_score_main.append((0,0,data))
        
        
        max_comp_scr = 10 * len(compliance_vals)
        for data in compliance_vals:
            sal_val_percent =0.0
            sale_value  = data.get('sale_value')
            if tot_sal_comp:
                sal_val_percent = sale_value/float(tot_sal_comp)
            score = data.get('score')
            weight_comp = max_comp_scr * sal_val_percent * (score/10.0)
            data['sale_value_percent'] = sal_val_percent *100.0
            data['weight'] = weight_comp
            comp_weight.append(weight_comp)
            compliance_vals_main.append((0,0,data))
        
        day_weight_scr = self.get_avg_score(day_weight)
        comp_weight_scr = self.get_avg_score(comp_weight )
        cert_score =0.0
        day_flag = comp_flag =cert_flag=hd_flag=  False
        if day_score_main:
            day_flag =True 
        if compliance_vals_main:
            comp_flag = True
        employee = self.search([('user_id','=',user_id)],limit=1)
        cert = employee.get_certificate_status()
        cert_ach = cert.get('achieved',False)
        cert_req = cert.get('required',False)
        
        if cert_req:
            cert_flag = True
        if cert_ach:
            cert_score =100.0
        
        hd_vals,hd_score = self.get_hd_data(sample_id, user_id, aud_date_start, aud_date_end, audit_temp_id)
        if hd_vals:
            hd_flag = True
        
        comp_line = self.get_sde_component(day_weight_scr,comp_weight_scr,hd_score,cert_score,day_flag,comp_flag,hd_flag,cert_flag)
        
        return day_score_main,hd_vals,compliance_vals_main,comp_line
    
    def get_pdm_data(self,sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id):
        employee_id = self.id
        team_ids = self.search([('parent_id','=',employee_id)]) 
        user_ids = [emp.user_id.id for emp in team_ids if (emp.audit_temp_id and emp.audit_temp_id.type=='pm') ] + [user_id]
        result = []
        team_vals =[]
        score_board =[] 
        day_score_vals = cost_control_vals = invoice_schedule_vals = compliance_vals = schedule_control_vals = my_comp_data=[]
        for uid in user_ids:
            day_score_main,cost_control_val_main,invoice_schedule_main,compliance_vals_main,schedule_control_vals_main,team_comp_data = self.get_pm_data(sample_id,uid, aud_date_start, aud_date_end, audit_temp_id)
            if uid == user_id:
                day_score_vals, cost_control_vals,invoice_schedule_vals,compliance_vals, schedule_control_vals,my_comp_data = day_score_main,cost_control_val_main,invoice_schedule_main,compliance_vals_main,schedule_control_vals_main,team_comp_data
            score = self.get_score_from_comp_data(team_comp_data)
            team_vals.append((0,0,{'user_id':uid,'score':score}))
            score_board.append(score)

            
        team_avg_score =  self.get_avg_score(score_board)  
        comp_line =[(0,0,{'name':'Average Of Team Performance','weight':100,'score':team_avg_score,'final_score':team_avg_score})]
        return day_score_vals,cost_control_vals,invoice_schedule_vals,compliance_vals, schedule_control_vals,team_vals,my_comp_data,comp_line
        
        
    def get_bdm_component(self,total_gp):
        target = self.annual_target/12.0
        result =0.0
        
        comp_data = []
        wt_lead = .9 
        wt_cert = .1
        cert_score = 0.0
        cert = self.get_certificate_status()
        cert_ach = cert.get('achieved',False)
        cert_req = cert.get('required',False)
        if cert_ach:
            cert_score =100
        if target:
            result = total_gp/target 
            if result >1.5:
                result =1.5
        
        if not cert_req:
            wt_lead =1
            wt_cert =0.0 
        if wt_lead:
            score = result *100
            final_score = score * wt_lead
            comp_data.append((0,0,{'name':'Lead Performance','score':score,'weight':wt_lead*100.0,'final_score':final_score}))
        if wt_cert:
            score = cert_score
            final_score = score * wt_cert
            comp_data.append((0,0,{'name':'Career Certificate','score':score,'weight':wt_cert*100.0,'final_score':final_score}))
        return comp_data,target
            
    
    def get_bdm_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        result =[]
        total_gp =0.0
        user_id  = self.user_id and self.user_id.id
        domain = [('lead_created_by','=',user_id),('status','=','active')]
        domain.extend([('submit_to_customer_date','>=',aud_date_start),('submit_to_customer_date','<=',aud_date_end)])
        domain1 = domain + [('state','in',('submitted','handover','processed'))]
        sheet_ids =self.env['od.cost.sheet'].search(domain1)
        for sheet in sheet_ids:
            gp = sheet.total_gp
            result.append((0,0,{'cost_sheet_id':sheet.id,'gp':sheet.total_gp}))
            total_gp +=gp
        comp_data,target = self.get_bdm_component(total_gp)
        return result,comp_data,target
        
    
    
    def get_bdm_sec_pip_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        result =[]
        
       
        domain = [('status','=','active')]
        domain.extend([('submit_to_customer_date','>=',aud_date_start),('submit_to_customer_date','<=',aud_date_end)])
        domain1 = domain + [('state','in',('submitted','handover','processed'))]
        sheet_ids =self.env['od.cost.sheet'].search(domain1)
        for sheet in sheet_ids:
            sheet.update_cost_sheet()
            for line in sheet.summary_weight_line:
                if line.pdt_grp_id.id ==2:
                    gp = line.total_gp
                    result.append((0,0,{'cost_sheet_id':sheet.id,'gp':line.total_gp,'sales':line.total_sale,
                                        'sales_aftr_disc':line.sale_aftr_disc,'cost':line.total_cost,'profit':line.profit,'profit_percent':line.profit_percent,'manpower_cost':line.manpower_cost,'product_group_id':line.pdt_grp_id.id}))
                   
       
        return result
    
    
    def get_bdm_sec_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        result =[]
        total_gp =0.0
        user_id  = self.user_id and self.user_id.id
        domain = [('lead_created_by','=',user_id),('status','=','active')]
        domain.extend([('submit_to_customer_date','>=',aud_date_start),('submit_to_customer_date','<=',aud_date_end)])
        domain1 = domain + [('state','not in',('draft','design_ready','cancelled'))]
        sheet_ids =self.env['od.cost.sheet'].search(domain1)
        for sheet in sheet_ids:
            sheet.update_cost_sheet()
            for line in sheet.summary_weight_line:
                if line.pdt_grp_id.id ==2:
                    gp = line.total_gp
                    result.append((0,0,{'cost_sheet_id':sheet.id,'gp':line.total_gp,'sales':line.total_sale,'sales_aftr_disc':line.sale_aftr_disc,'cost':line.total_cost,
                                        'profit':line.profit,'profit_percent':line.profit_percent,'manpower_cost':line.manpower_cost,'product_group_id':line.pdt_grp_id.id}))
                    total_gp +=gp
        comp_data,target = self.get_bdm_component(total_gp)
        return result,comp_data,target
    
    def get_bdm_net_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        result =[]
        total_gp =0.0
        user_id  = self.user_id and self.user_id.id
        domain = [('lead_created_by','=',user_id),('status','=','active')]
        domain.extend([('submit_to_customer_date','>=',aud_date_start),('submit_to_customer_date','<=',aud_date_end)])
        domain1 = domain + [('state','not in',('draft','design_ready','cancelled'))]
        sheet_ids =self.env['od.cost.sheet'].search(domain1)
        for sheet in sheet_ids:
            sheet.update_cost_sheet()
            for line in sheet.summary_weight_line:
                if line.pdt_grp_id.id in (1,3):
                    gp = line.total_gp
                    result.append((0,0,{'cost_sheet_id':sheet.id,'gp':line.total_gp,'sales':line.total_sale,'sales_aftr_disc':line.sale_aftr_disc,'cost':line.total_cost,
                                        'profit':line.profit,'profit_percent':line.profit_percent,'manpower_cost':line.manpower_cost,'product_group_id':line.pdt_grp_id.id}))
                    total_gp +=gp
        comp_data,target = self.get_bdm_component(total_gp)
        return result,comp_data,target        
    
    def get_bdm_net_pip_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        result =[]
        
        user_id  = self.user_id and self.user_id.id
        domain = [('status','=','active')]
        domain.extend([('submit_to_customer_date','>=',aud_date_start),('submit_to_customer_date','<=',aud_date_end)])
        domain1 = domain + [('state','in',('submitted','handover','processed'))]
        sheet_ids =self.env['od.cost.sheet'].search(domain1)
        for sheet in sheet_ids:
            sheet.update_cost_sheet()
            for line in sheet.summary_weight_line:
                if line.pdt_grp_id.id in (1,3):
                    gp = line.total_gp
                    result.append((0,0,{'cost_sheet_id':sheet.id,'gp':line.total_gp,'sales':line.total_sale,'sales_aftr_disc':line.sale_aftr_disc,'cost':line.total_cost,
                                        'profit':line.profit,'profit_percent':line.profit_percent,'manpower_cost':line.manpower_cost,'product_group_id':line.pdt_grp_id.id}))
                  
        return result
    
    
    
    def get_supplier_paid(self,supplier_invoice):
        paid = 0.0
        for sup_inv in supplier_invoice:
            currency = sup_inv.currency_id
            company_currency = sup_inv.company_id.currency_id
            bal  = sup_inv.amount_total - sup_inv.residual 
            paid += currency.compute(bal,company_currency,round=False)
        return paid
    
    def get_supplier_amount(self,supplier_invoice):
        amount = 0.0
        for sup_inv in supplier_invoice:
            currency = sup_inv.currency_id
            company_currency = sup_inv.company_id.currency_id
            bal  = sup_inv.amount_total
            amount += currency.compute(bal,company_currency,round=False)
        return amount
    def get_pmo_dir_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        open_projects = []
        closed_projects =[]
        analytic_pool = self.env['account.analytic.account']
        company_id = self.company_id and self.company_id.id
        open_project_ids = analytic_pool.search([('company_id','=',company_id),('od_type_of_project','not in',('amc','o_m','credit','comp_gen')),('state','not in',('close','cancelled'))])
        closed_project_ids = analytic_pool.search([('company_id','=',company_id),('od_type_of_project','not in',('amc','o_m','credit','comp_gen')),('state','=','close')])
        sale_pool = self.env['sale.order']
        invoice_pool = self.env['account.invoice']
        total_collected =0.0
        total_paid =0.0
        timesheet_pool = self.env['hr.analytic.timesheet']
        for project in open_project_ids:
            sale = sale_pool.search([('project_id','=',project.id),('state','!=','cancel')],limit=1)
            amount_total = sale.amount_total or 0.0
            discount = abs(sale.od_discount) or 0.0
            project_value = amount_total - discount
            customer_invoice = invoice_pool.search([('od_analytic_account','=',project.id),('type','=','out_invoice'),('state','not in',('draft','cancel'))])
            supplier_invoice = invoice_pool.search([('od_analytic_account','=',project.id),('type','=','in_invoice'),('state','not in',('draft','cancel'))])
            collected = sum([inv.amount_total - inv.residual for inv in customer_invoice])
#             paid = sum([inv.amount_total - inv.residual for inv in supplier_invoice])
            paid = self.get_supplier_paid(supplier_invoice)
            total_collected += collected
            total_paid += paid
            manpower_cost = sum([tm.normal_amount for tm in timesheet_pool.search([('account_id','=',project.id),('date','<=',aud_date_end)])])
            total_paid += manpower_cost
            open_projects.append((0,0,{'analytic_id':project.id,'project_value':project_value,'collected':collected,'paid':paid,'manpower_cost':manpower_cost}))
            
        for project in closed_project_ids:
            sale = sale_pool.search([('project_id','=',project.id),('state','!=','cancel')],limit=1)
            amount_total = sale.amount_total or 0.0
            discount = abs(sale.od_discount) or 0.0
            project_value = amount_total - discount
            customer_invoice = invoice_pool.search([('od_analytic_account','=',project.id),('type','=','out_invoice'),('state','not in',('draft','cancel'))])
            customer_refund = invoice_pool.search([('od_analytic_account','=',project.id),('type','=','out_refund'),('state','not in',('draft','cancel'))])
            supplier_invoice = invoice_pool.search([('od_analytic_account','=',project.id),('type','=','in_invoice'),('state','not in',('draft','cancel'))])
            supplier_refund= invoice_pool.search([('od_analytic_account','=',project.id),('type','=','in_refund'),('state','not in',('draft','cancel'))])
            customer_inv_amount = sum([inv.amount_total for inv in customer_invoice])
            supplier_inv_amount =self.get_supplier_amount(supplier_invoice)
            manpower_cost = sum([tm.normal_amount for tm in timesheet_pool.search([('account_id','=',project.id),('date','<=',aud_date_end)])])
            customer_refund_amount = sum([inv.amount_total - inv.residual for inv in customer_refund])
#             supplier_refund_amount =sum([inv.amount_total - inv.residual for inv in supplier_refund])
            supplier_refund_amount = self.get_supplier_paid(supplier_refund)
            collected = sum([inv.amount_total - inv.residual for inv in customer_invoice])
            paid = self.get_supplier_paid(supplier_invoice)
            collected = collected - customer_refund_amount
            paid = paid - supplier_refund_amount
            
            if collected == customer_inv_amount and supplier_inv_amount== paid:
                continue
            total_paid += project_value
            total_paid += manpower_cost
            total_collected += collected
            closed_projects.append((0,0,{'analytic_id':project.id,'project_value':project_value,'collected':collected,'paid':paid,'manpower_cost':manpower_cost})) 
        res =0.0
        if total_paid:
            res = total_collected/float(total_paid)
        comp_line =[(0,0,{'name':'Cash Flow Management','weight':100,'score':res*100.0,'final_score':res*100.0})]
        return open_projects,closed_projects,comp_line
    
    
    def get_score_from_comp_data(self,vals):
        res =0.0
        for _,_,val in vals:
            final_score = val.get('final_score',0.0)
            res += final_score 
        return res
    
    def get_tc_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        opp_sample_line,team_line,presale_comp_data = self.get_presale_mgr_vals_tc(sample_id, aud_date_start, aud_date_end, audit_temp_id)
        utl_data,fot_data,tech_comp_data = self.get_tech_cons_ps_vals(sample_id, aud_date_start, aud_date_end, audit_temp_id)
        presale_score = self.get_score_from_comp_data(presale_comp_data)
        tech_score = self.get_score_from_comp_data(tech_comp_data)
        wt_tech =0.7
        wt_presale =0.3
        comp_line =[(0,0,{'name':'Technical Activity','weight':wt_tech *100,'score':tech_score,'final_score':wt_tech * tech_score}),
                    (0,0,{'name':'Pre-sale Productivity','weight':wt_presale *100,'score':presale_score,'final_score':wt_presale * presale_score})
                    ]
        return opp_sample_line,team_line,presale_comp_data,utl_data,fot_data,tech_comp_data,comp_line
        
    def update_audit_sample(self,sample_id,aud_date_start,aud_date_end,audit_temp_id):
        type = audit_temp_id.type
        user_id  = self.user_id and self.user_id.id
        employee_id = self.id
        dt_start = aud_date_start
        result = []
        if type =='post_sales':
            result,comp_data,utilization = self.get_post_sales_vals(sample_id, aud_date_start, aud_date_end)
            sample_id.post_sale_sample_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'post_sale_sample_line':result,'comp_line':comp_data,'utilization':utilization})
        
        if type =='ttl':
            result,fot_data,comp_data = self.get_ttl_vals(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.utl_sample_line.unlink()
            sample_id.ttl_fot_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'utl_sample_line':result,'ttl_fot_line':fot_data,'comp_line':comp_data})
        
        if type == 'pre_sales':
            opp_sample_line,comp_data = self.get_presale_vals(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.opp_sample_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'opp_sample_line':opp_sample_line,'comp_line':comp_data})
        if type  == 'pre_sales_mgr':
            opp_sample_line,team_line,comp_data = self.get_presale_mgr_vals(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.opp_sample_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.team_line.unlink()
            sample_id.write({'opp_sample_line':opp_sample_line,'comp_line':comp_data,'team_line':team_line})
        if type =='tc':
            opp_sample_line,team_line,presale_comp_data,utl_data,fot_data,tech_comp_data,comp_line = self.get_tc_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.utl_sample_line.unlink()
            sample_id.ttl_fot_line.unlink()
            sample_id.opp_sample_line.unlink()
            
            sample_id.tc_tech_comp_line.unlink()
            sample_id.tc_presale_comp_line.unlink()
            
            sample_id.team_line.unlink()
            sample_id.comp_line.unlink()
            
            sample_id.write({'utl_sample_line':utl_data,'ttl_fot_line':fot_data,
                             'opp_sample_line':opp_sample_line,'comp_line':comp_line,
                             'tc_tech_comp_line':tech_comp_data,
                             'tc_presale_comp_line':presale_comp_data,
                             'team_line':team_line})
        
        
        if type == 'sales_acc_mgr':
            
            achieved_line,achieved_total = self.get_sales_achieved_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            commit_total = sample_id.commit_total
            component_data,target = self.get_sales_acc_mgr_component(commit_total,achieved_total)
            sample_id.comp_line.unlink()
            sample_id.achieved_gp_line.unlink()
            sample_id.write({'achieved_gp_line':achieved_line,'comp_line':component_data,'target':target})
            self.write({'commit_total':commit_total})
        
        if type == 'sm':
            achieved_gp_line,team_line,comp_line = self.get_sm_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.comp_line.unlink()
            sample_id.achieved_gp_line.unlink()
            sample_id.team_line.unlink()
            sample_id.write({'achieved_gp_line':achieved_gp_line,'comp_line':comp_line,'team_line':team_line})
        if type == 'pm':

            day_score_vals,cost_control_vals,invoice_schedule_vals,compliance_vals,pm_sch_line,comp_line = self.get_pm_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.dayscore_line.unlink()
            sample_id.cost_control_line.unlink()
            sample_id.invoice_schedule_line.unlink()
            sample_id.compliance_line.unlink()
            sample_id.pm_sch_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'dayscore_line':day_score_vals,'cost_control_line':cost_control_vals,
                             'invoice_schedule_line':invoice_schedule_vals,
                             'pm_sch_line':pm_sch_line,
                             'compliance_line':compliance_vals,'comp_line':comp_line})
            
        
        if type == 'sde':
            day_score_vals,hd_line,compliance_vals,comp_line = self.get_sde_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.dayscore_line.unlink()
            sample_id.hd_line.unlink()
            sample_id.compliance_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'dayscore_line':day_score_vals,'hd_line':hd_line,
                         'compliance_line':compliance_vals,'comp_line':comp_line})
            
        if type == 'sdm':
            team_day_line,team_hd_line,comp_line = self.get_sdm_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.comp_line.unlink()
            sample_id.team_hd_line.unlink()
            sample_id.team_day_line.unlink()
            sample_id.write({'team_day_line':team_day_line,'comp_line':comp_line,'team_hd_line':team_hd_line})
            
        
        if type == 'pdm':
            day_score_vals,cost_control_vals,invoice_schedule_vals,compliance_vals,pm_sch_line,team_line,my_comp_line,comp_line = self.get_pdm_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.dayscore_line.unlink()
            sample_id.cost_control_line.unlink()
            sample_id.invoice_schedule_line.unlink()
            sample_id.compliance_line.unlink()
            sample_id.pm_sch_line.unlink()
            sample_id.my_comp_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.team_line.unlink()
            sample_id.write({'dayscore_line':day_score_vals,'cost_control_line':cost_control_vals,
                             'invoice_schedule_line':invoice_schedule_vals,
                             'pm_sch_line':pm_sch_line,
                             'compliance_line':compliance_vals,'team_line':team_line,'my_comp_line':my_comp_line,'comp_line':comp_line})
        
        if type == 'bdm':
            bmd_costsheet_line,comp_line,target = self.get_bdm_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.bmd_costsheet_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'bmd_costsheet_line':bmd_costsheet_line,'comp_line':comp_line,'target':target})
        if type == 'bdm_sec':
            bdm_sec_sample_line,comp_line,target = self.get_bdm_sec_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            pipline_data = self.get_bdm_sec_pip_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.bdm_sec_sample_line.unlink()
            sample_id.bdm_sec_pip_sample_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'bdm_sec_sample_line':bdm_sec_sample_line,'comp_line':comp_line,'target':target,'bdm_sec_pip_sample_line':pipline_data})

        if type == 'bdm_net':
            bdm_net_sample_line,comp_line,target = self.get_bdm_net_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            pipline_data = self.get_bdm_net_pip_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.bdm_net_sample_line.unlink()
            sample_id.bdm_net_pip_sample_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'bdm_net_sample_line':bdm_net_sample_line,'comp_line':comp_line,'target':target,'bdm_net_pip_sample_line':pipline_data})
        
        
        
        if type == 'pmo':
            pmo_open_project_line,pmo_closed_project_line,comp_line = self.get_pmo_dir_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.pmo_open_project_line.unlink()
            sample_id.pmo_closed_project_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'pmo_open_project_line':pmo_open_project_line,'comp_line':comp_line,'pmo_closed_project_line':pmo_closed_project_line})
        
        if type == 'hoo':
            utl_sample_line,ttl_fot_line,pmo_open_project_line,pmo_closed_project_line,team_line,ttl_comp_line = self.get_hoo_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            sample_id.pmo_open_project_line.unlink()
            sample_id.pmo_closed_project_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.team_line.unlink()
            sample_id.utl_sample_line.unlink()
            sample_id.ttl_fot_line.unlink()
            sample_id.write({'utl_sample_line':utl_sample_line,'ttl_fot_line':ttl_fot_line,
                         'pmo_open_project_line':pmo_open_project_line,'pmo_closed_project_line':pmo_closed_project_line,
                         'team_line':team_line,
                         'comp_line':ttl_comp_line}) 
        
    
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
            result,comp_data,utilization = self.get_post_sales_vals(sample_id, aud_date_start, aud_date_end)
            vals.update({'post_sale_sample_line':result,'comp_line':comp_data,'utilization':utilization})
            sample_id =self.env['audit.sample'].create(vals)
        
        
        if type =='ttl':
            result,fot_data,comp_data = self.get_ttl_vals(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'utl_sample_line':result,'ttl_fot_line':fot_data,'comp_line':comp_data}) 
            sample_id =self.env['audit.sample'].create(vals)
        
        if type == 'hoo':
            utl_sample_line,ttl_fot_line,pmo_open_project_line,pmo_closed_project_line,team_line,ttl_comp_line = self.get_hoo_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'utl_sample_line':utl_sample_line,'ttl_fot_line':ttl_fot_line,
                         'pmo_open_project_line':pmo_open_project_line,'pmo_closed_project_line':pmo_closed_project_line,
                         'team_line':team_line,
                         'comp_line':ttl_comp_line}) 
            sample_id =self.env['audit.sample'].create(vals)
            
        if type == 'pre_sales':
            opp_sample_line,comp_data = self.get_presale_vals(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'opp_sample_line':opp_sample_line,'comp_line':comp_data}) 
            sample_id =self.env['audit.sample'].create(vals)
            
        if type  == 'pre_sales_mgr':
            opp_sample_line,team_line,comp_data = self.get_presale_mgr_vals(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'opp_sample_line':opp_sample_line,'comp_line':comp_data,'team_line':team_line}) 
            sample_id =self.env['audit.sample'].create(vals)
            #create utlization line
        
        if type == 'tc':
            opp_sample_line,team_line,presale_comp_data,utl_data,fot_data,tech_comp_data,comp_line = self.get_tc_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'utl_sample_line':utl_data,'ttl_fot_line':fot_data,
                             'opp_sample_line':opp_sample_line,'comp_line':comp_line,
                             'tc_tech_comp_line':tech_comp_data,
                             'tc_presale_comp_line':presale_comp_data,
                             'team_line':team_line})
            sample_id =self.env['audit.sample'].create(vals)
        if type == 'sales_acc_mgr':
            commit_line,commit_total = self.get_sales_commit_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            achieved_line,achieved_total = self.get_sales_achieved_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            component_data,target = self.get_sales_acc_mgr_component(commit_total,achieved_total)
            vals.update({'commit_gp_line':commit_line,'achieved_gp_line':achieved_line,'comp_line':component_data,'target':target})
            sample_id =self.env['audit.sample'].create(vals)
            self.write({'commit_total':commit_total})
        
        if type == 'sm':
            achieved_gp_line,team_line,comp_line = self.get_sm_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'achieved_gp_line':achieved_gp_line,'comp_line':comp_line,'team_line':team_line})
            sample_id =self.env['audit.sample'].create(vals)
        
        
        
        if type == 'pm':
            
            day_score_vals,cost_control_vals,invoice_schedule_vals,compliance_vals,pm_sch_line,comp_line = self.get_pm_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'dayscore_line':day_score_vals,'cost_control_line':cost_control_vals,'invoice_schedule_line':invoice_schedule_vals,
                         'compliance_line':compliance_vals,'pm_sch_line':pm_sch_line,'comp_line':comp_line})
            sample_id =self.env['audit.sample'].create(vals)
        
        if type == 'sde':
            day_score_vals,hd_line,compliance_vals,comp_line = self.get_sde_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'dayscore_line':day_score_vals,'hd_line':hd_line,
                         'compliance_line':compliance_vals,'comp_line':comp_line})
            sample_id =self.env['audit.sample'].create(vals)
            
        if type == 'sdm':
            team_day_line,team_hd_line,comp_line = self.get_sdm_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'team_day_line':team_day_line,'comp_line':comp_line,'team_hd_line':team_hd_line})
            sample_id =self.env['audit.sample'].create(vals)
        
        
        if type == 'pmo':
            pmo_open_project_line,pmo_closed_project_line,comp_line = self.get_pmo_dir_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'pmo_open_project_line':pmo_open_project_line,'pmo_closed_project_line':pmo_closed_project_line,'comp_line':comp_line})
            sample_id =self.env['audit.sample'].create(vals)
            
        if type == 'pdm':
            day_score_vals,cost_control_vals,invoice_schedule_vals,compliance_vals,pm_sch_line,team_line,my_comp_line,comp_line = self.get_pdm_data(sample_id,user_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'dayscore_line':day_score_vals,'cost_control_line':cost_control_vals,'invoice_schedule_line':invoice_schedule_vals,
                         'compliance_line':compliance_vals,'pm_sch_line':pm_sch_line,'team_line':team_line,'my_comp_line':my_comp_line,'comp_line':comp_line})
            sample_id =self.env['audit.sample'].create(vals)
            
        if type == 'bdm':
            bmd_costsheet_line,comp_line,target = self.get_bdm_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'bmd_costsheet_line':bmd_costsheet_line,'comp_line':comp_line,'target':target})
            sample_id =self.env['audit.sample'].create(vals)
        
        if type == 'bdm_sec':
            bdm_sec_sample_line,comp_line,target = self.get_bdm_sec_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            pipline_data = self.get_bdm_sec_pip_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'bdm_sec_sample_line':bdm_sec_sample_line,'comp_line':comp_line,'target':target,'bdm_sec_pip_sample_line':pipline_data})
            sample_id =self.env['audit.sample'].create(vals)
        
        if type == 'bdm_net':
            bdm_net_sample_line,comp_line,target = self.get_bdm_net_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            pipline_data = self.get_bdm_net_pip_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'bdm_net_sample_line':bdm_net_sample_line,'comp_line':comp_line,'target':target,'bdm_net_pip_sample_line':pipline_data})
            sample_id =self.env['audit.sample'].create(vals)
        
        return sample_id
    
    
    
    
    
    
    def get_certificate_status(self):
        res={}
        ex_num = self.get_execution_number()
        ex_num = str(ex_num)
        cert='cert'+ ex_num
        cert_st ='cert_status'+ex_num
        if eval('self.'+cert):
            res['required'] = True 
            if eval('self.'+cert_st) == 'achieved':
                res['achieved'] =True
        return res
    def get_mgr_feedback(self):
        result =0.0
        ex_num = self.get_execution_number()
        ex_num = str(ex_num)
        feedback='mgr_feedback'+ ex_num
        score ='mgr_score'+ex_num
        if eval('self.'+feedback):
            result = eval('self.'+score) 
        return result
            
        
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
            utl ='utl'+ex_num
            if aud_samp_check:
                sample_id  = eval('self.'+aud_samp)
                self.update_audit_sample(sample_id,aud_date_start,aud_date_end,audit_temp_id)
#                 score =  self.get_score(sample_id.avg_score, type, ex_num)
                score = sample_id.avg_score
                utilization = sample_id.utilization
                self.write({scr:score,utl:utilization})
            else:
                sample_id =self.create_audit_sample(aud_date_start,aud_date_end,audit_temp_id)
                if sample_id:
#                     score =  self.get_score(sample_id.avg_score, type, ex_num)
                    score = sample_id.avg_score
                    utilization = sample_id.utilization
                    self.write({aud_samp:sample_id.id,scr:score,utl:utilization})
     
    
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
    def audit_set_execution(self,number=False):
        today = dt.today()
        month_number = today.month
       
        day = today.day 
        if day >27:
            month_number +=1
        if number:
            month_number = number
        ext ='execute'+str(month_number)
        self.write({ext:True})
        for i in range(1,13):
            if i != month_number:
                ext = 'execute'+str(i)
                self.write({ext:False})
        
        
        
        
        
