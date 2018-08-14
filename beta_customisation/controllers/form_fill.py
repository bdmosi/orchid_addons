# -*- coding: utf-8 -*-
import base64

from openerp import SUPERUSER_ID
from openerp import http
from openerp.tools.translate import _
from openerp.http import request
from openerp.addons.website.models.website import slug
from openerp import api

class BetaJoin(http.Controller):
    @http.route('/beta_join/<model("od.beta.joining.form"):join_id>', type='http', auth="public", website=True)
    def beta_join_form(self, join_id):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        orm_country = registry.get('res.country')
        country_ids = orm_country.search(cr, SUPERUSER_ID, [], context=context)
        countries = orm_country.browse(cr, SUPERUSER_ID, country_ids, context)
        
        error = {}
        default = {}
        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('consyshr_error')
            default = request.session.pop('consyshr_default')
        return request.render("beta_customisation.employee_join_form", {
            'joinee': join_id,
            'error':error,
            'default':default,
            'countries': countries,
        
        })

    @http.route('/beta_join/thankyou', methods=['POST'], type='http', auth="public", website=True)
    def jobs_thankyou(self, **post):
        error = {}
        for field_name in ["name", "personal_email"]:
            if not post.get(field_name):
                error[field_name] = 'missing'

        env = request.env(user=SUPERUSER_ID)
        value = {
        }
        for f in ['personal_email', 'name', 'dob','age','gender', 'father_name', 'passport_no', 'place_of_birth', 'martial', 'mobile', 'nationality', 'mobile']:
            value[f] = post.get(f)
        for f in ['join_id']:
            join_id = int(post.get(f) or False)
            emp_join_form_rec=env['od.beta.joining.form'].browse(join_id)
        # Retro-compatibility for saas-3. "phone" field should be replace by "partner_phone" in the template in trunk.
#         value['partner_phone'] = post.pop('phone', False)

        emp_join_id = emp_join_form_rec.write(value)
        if post['ufile']:
            attachment_value = {
                'name': post['ufile'].filename,
                'res_name': value['name'],
                'res_model': 'hr.applicant',
                'res_id': join_id,
                'datas': base64.encodestring(post['ufile'].read()),
                'datas_fname': post['ufile'].filename,
            }
            env['ir.attachment'].create(attachment_value)
        return request.render("beta_customisation.beta_thankyou", {})

# vim :et:
