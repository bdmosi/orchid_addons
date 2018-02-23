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
    
    
    
    def get_post_sales_vals(self,sample_id,aud_date_start,aud_date_end):
        user_id  = self.user_id and self.user_id.id
        result = []
        data_model = 'project.task'
        domain = [('od_type','=','activities'),('user_id','=',user_id),('od_stage','=','done')]
        aud_date_start = aud_date_start +' 04:00:00'
        aud_date_end = aud_date_end + ' 23:58:58'
        domain.extend([('date_start','>=',aud_date_start),('date_start','<=',aud_date_end)]) 
        data_ids =self.env[data_model].search(domain)
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
        avg_score =sum(score_board)/float(len(score_board))
        comp_data.append((0,0,{'name':'Activity Integrity','weight':wt_task,'score':avg_score,'final_score':(wt_task/100.0)*avg_score}))
        if wt_cert:
            comp_data.append((0,0,{'name':'Certificate','weight':wt_cert,'score':cert_score,'final_score':(wt_cert/100.0)*cert_score}))
        return result,comp_data
        
    
    
    
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
        
        
    def get_ttl_vals(self,sample_id,aud_date_start,aud_date_end,audit_temp_id):
        type = audit_temp_id.type
        user_id  = self.user_id and self.user_id.id
        employee_id = self.id
        dt_start = aud_date_start
        result = []
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
            result.append((0,0,{'user_id':user_id,'available_time':avl_time,'actual_time_spent':spent_time,'utl':(spent_time/avl_time)*100.0}))
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
            comp_data.append((0,0,{'name':'Percentage Of Cancelled Activities','weight':wt_tsk_cncl,'score':tsk_cncl_scr,'final_score':wt_tsk_cncl * tsk_cncl_scr}))
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
        avg_score = sum(score_boards)/float(len(score_boards))
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
        avg_score = sum(score_boards)/float(len(score_boards))
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
    
    def get_presale_mgr_vals(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        user_id  = self.user_id and self.user_id.id
        employee_id = self.id
        team_ids = self.search([('parent_id','=',employee_id)]) 
        user_ids = [emp.user_id.id for emp in team_ids] + [user_id]
        result = []
        team_score =[]
        team_vals =[] 
        for uid in user_ids:
            data,avg_score = self.get_presale_data(uid, aud_date_start, aud_date_end, audit_temp_id)
            team_score.append(avg_score)
            team_vals.append((0,0,{'user_id':uid,'score':avg_score}))
            result.extend(data)
            
        team_avg_score = sum(team_score)/float(len(team_score))
        comp_data =[(0,0,{'name':'Productivity','weight':100,'score':team_avg_score,'final_score':team_avg_score})]
        return result,team_vals,comp_data
    def get_sales_commit_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        
        total_gp = 0.0
        user_id  = self.user_id and self.user_id.id
        result =[]
        domain = [('sales_acc_manager','=',user_id)]
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
                result.append((0,0,{'cost_sheet_id':sheet.id,'gp':gp}))
                total_gp +=gp
        return result,total_gp
    def get_sales_achieved_data(self,sample_id, aud_date_start, aud_date_end, audit_temp_id):
        user_id  = self.user_id and self.user_id.id
        result =[]
        total_gp = 0.0
        domain = [('sales_acc_manager','=',user_id)]
        domain.extend([('op_expected_booking','>=',aud_date_start),('op_expected_booking','<=',aud_date_end)])
        domain1 = domain + [('state','in',('approved','done','modify','change','analytic_change'))]
        sheet_ids =self.env['od.cost.sheet'].search(domain1)
        for sheet in sheet_ids:
            gp = sheet.total_gp
            result.append((0,0,{'cost_sheet_id':sheet.id,'gp':sheet.total_gp}))
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
                               'final_score':(wt_cert/100)*cert_score}
                              ))
        if mgr_score:
            comp_data.append((0,0,
                              {'name':'Direct Manager Feedback',
                               'weight':wt_mgr,
                               'score':mgr_score*10,
                               'final_score':mgr_score}
                              ))
        
        return comp_data
            
        
            
        
    
    def update_audit_sample(self,sample_id,aud_date_start,aud_date_end,audit_temp_id):
        type = audit_temp_id.type
        user_id  = self.user_id and self.user_id.id
        employee_id = self.id
        dt_start = aud_date_start
        result = []
        if type =='post_sales':
            result,comp_data = self.get_post_sales_vals(sample_id, aud_date_start, aud_date_end)
            sample_id.post_sale_sample_line.unlink()
            sample_id.comp_line.unlink()
            sample_id.write({'post_sale_sample_line':result,'comp_line':comp_data})
        
        if type =='ttl':
            result,fot_data,comp_data = self.get_ttl_vals(sample_id, aud_date_start, aud_date_end, audit_temp_id)
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
            
        if type == 'sales_acc_mgr':
            
            achieved_line,achieved_total = self.get_sales_achieved_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            commit_total = sample_id.commit_total
            component_data = self.get_sales_acc_mgr_component(commit_total,achieved_total)
            sample_id.comp_line.unlink()
            sample_id.achieved_gp_line.unlink()
            sample_id.write({'achieved_gp_line':achieved_line,'comp_line':component_data,})
           
    
    
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
            result,comp_data = self.get_post_sales_vals(sample_id, aud_date_start, aud_date_end)
            vals.update({'post_sale_sample_line':result,'comp_line':comp_data})
            sample_id =self.env['audit.sample'].create(vals)
        
        
        if type =='ttl':
            result,fot_data,comp_data = self.get_ttl_vals(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            vals.update({'utl_sample_line':result,'ttl_fot_line':fot_data,'comp_line':comp_data}) 
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
        
        
        if type == 'sales_acc_mgr':
            commit_line,commit_total = self.get_sales_commit_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            achieved_line,achieved_total = self.get_sales_achieved_data(sample_id, aud_date_start, aud_date_end, audit_temp_id)
            component_data = self.get_sales_acc_mgr_component(commit_total,achieved_total)
            vals.update({'commit_gp_line':commit_line,'achieved_gp_line':achieved_line,'comp_line':component_data})
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
            if aud_samp_check:
                sample_id  = eval('self.'+aud_samp)
                self.update_audit_sample(sample_id,aud_date_start,aud_date_end,audit_temp_id)
#                 score =  self.get_score(sample_id.avg_score, type, ex_num)
                score = sample_id.avg_score
                self.write({scr:score})
            else:
                sample_id =self.create_audit_sample(aud_date_start,aud_date_end,audit_temp_id)
                if sample_id:
#                     score =  self.get_score(sample_id.avg_score, type, ex_num)
                    score = sample_id.avg_score
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
        
        
        
        
        
