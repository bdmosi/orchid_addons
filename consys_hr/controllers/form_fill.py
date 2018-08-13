# -*- coding: utf-8 -*-
import base64

from openerp import SUPERUSER_ID
from openerp import http
from openerp.tools.translate import _
from openerp.http import request
from openerp.addons.website.models.website import slug
from openerp import api
class hr_form_fill(http.Controller):
    @http.route('/form/fill/<model("hr.employee"):employee>', type='http', auth="public", website=True)
    def fill_form(self, employee):
        error = {}
        default = {}
        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('consyshr_error')
            default = request.session.pop('consyshr_default')
        return request.render("consyshr.employee_form", {
            'employee': employee,
            'error':error,
            'default':default
        
        })

    @http.route('/formfill/thankyou', methods=['POST'], type='http', auth="public", website=True)
    def form_thankyou(self, **post):
        error = {}
#         for field_name in ["passport_id", "marital"]:
#             if not post.get(field_name):
#                 error[field_name] = 'missing'
#                 print "you got errorrrrrrrrrrrr"
        if error:
            request.session['consyshr_error'] = error
#             ufile = post.pop('ufile')
#             if ufile:
#                 error['ufile'] = 'reset'
            request.session['consyshr_default'] = post
            return request.redirect('/form/fill/%s' % post.get("employee_id"))

        # public user can't create applicants (duh)
        env = request.env(user=SUPERUSER_ID)
        employee_id = int(post.get('employee_id'))
        print "xxxxxxxxxxxxxxxxx",employee_id
#         for f in ["passport_id"]:
#             print "helllllllllllllooooooo",f
#             value[f] = post.get(f)
# #         for f in ['department_id', 'job_id']:
# #             value[f] = int(post.get(f) or 0)
#         # Retro-compatibility for saas-3. "phone" field should be replace by "partner_phone" in the template in trunk.
# #         value['partner_phone'] = post.pop('phone', False)
#         print "valueeeeeeeeeeeee",value
        emp=env['hr.employee'].browse(employee_id)
        emp.present_address = str(post.get('present_address'))
        emp.permanent_address = str(post.get('permanent_address'))
        emp.blood_group = str(post.get('blood_group'))
        emp.religion = str(post.get('religion'))
        emp.passport_id = str(post.get('passport_id'))
        emp.identification_id = str(post.get('identification_id'))
        emp.marital=str(post.get('marital'))
        emp.em_contact=str(post.get('em_contact'))
        emp.em_relation=str(post.get('em_relation'))
        emp.em_contact_no=str(post.get('em_contact_no'))
        emp.health = str(post.get('health'))
        if post.get('rowcount'):
            rowcount =int(post.get('rowcount'))
            vallist =[]
            for x in range(rowcount):
                val ={'employee_id':employee_id,'langauage':str(post.get('txt1_'+ str(x))),'can_speak':str(post.get('txt2_'+ str(x))),'can_read':str(post.get('txt3_'+ str(x))),'can_write':str(post.get('txt4_'+ str(x)))}
                vallist.append(val)
            for x in vallist:
                env['hr.emloyee.langauage'].create(x)
        if post.get('familycount'):
            familycount =int(post.get('familycount'))
            vallist =[]
            for x in range(familycount):
                val ={'employee_id':employee_id,'name':str(post.get('f1_'+ str(x))),'relationship':str(post.get('f2_'+ str(x))),'age':str(post.get('f3_'+ str(x))),'occupation':str(post.get('f4_'+ str(x))),'dependent':str(post.get('f5_'+ str(x)))}
                vallist.append(val)
            for x in vallist:
                env['hr.employee.family'].create(x)
        if post.get('academycount'):
            academycount =int(post.get('academycount'))
            vallist =[]
            for x in range(academycount):
                val ={'employee_id':employee_id,'from_date':str(post.get('a1_'+ str(x))),'to':str(post.get('a2_'+ str(x))),'degree':str(post.get('a3_'+ str(x))),'mark':str(post.get('a4_'+ str(x))),'regular':str(post.get('a5_'+ str(x)))}
                vallist.append(val)
            for x in vallist:
                env['hr.employee.academic'].create(x)
        if post.get('projectcount'):
            projectcount =int(post.get('projectcount')) 
            vallist =[]
            for x in range(projectcount):
                val ={'employee_id':employee_id,'from_date':str(post.get('p1_'+ str(x))),'to':str(post.get('p2_'+ str(x))),'institution':str(post.get('p3_'+ str(x))),'area':str(post.get('p4_'+ str(x)))}
                vallist.append(val)
            for x in vallist:
                env['hr.employee.project'].create(x)
#         if post['ufile']:
#             attachment_value = {
#                 'name': post['ufile'].filename,
#                 'res_name': value['partner_name'],
#                 'res_model': 'hr.applicant',
#                 'res_id': applicant_id,
#                 'datas': base64.encodestring(post['ufile'].read()),
#                 'datas_fname': post['ufile'].filename,
#             }
#             env['ir.attachment'].create(attachment_value)
        return request.render("consyshr.consyst_thankyou", {})

# vim :et:
