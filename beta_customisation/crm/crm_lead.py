# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2013 Camptocamp (<http://www.camptocamp.com>)
#    Authors: Ferdinand Gasauer, Joel Grand-Guillaume
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################
import datetime

from openerp.osv import fields, osv



class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    
    def run_employee_bday_reminder(self, cr, uid, context=None):
        template_id = self.pool['email.template'].browse(cr,uid,139)[0]
        hr_pool = self.pool['hr.employee']
        today = datetime.date.today()
        emp_ids=hr_pool.search(cr,uid,[],context=context)
        if emp_ids:
            for emp_id in emp_ids:
                emp_rec=hr_pool.browse(cr,uid,emp_id)
                birthday_date =emp_rec.birthday and datetime.datetime.strptime(emp_rec.birthday,'%Y-%m-%d')
                if birthday_date and birthday_date.month==today.month and  birthday_date.day == today.day:
                    self.pool.get('email.template').send_mail(cr, uid, template_id.id, emp_id, force_send=True, context=context)

class crm_lead(osv.osv):
    _inherit = "crm.lead"
    
    def action_schedule_meeting_lead(self, cr, uid, ids, context=None):
        """
        Open meeting's calendar view to schedule meeting on current lead.
        :return dict: dictionary value for created Meeting view
        """
        lead = self.browse(cr, uid, ids[0], context)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'calendar', 'action_calendar_event', context)
        partner_ids = [self.pool['res.users'].browse(cr, uid, uid, context=context).partner_id.id]
        if lead.partner_id:
            partner_ids.append(lead.partner_id.id)
        res['context'] = {
            'search_default_lead_id': lead.type == 'lead' and lead.id or False,
            'default_lead_id': lead.type == 'lead' and lead.id or False,
            'default_partner_id': lead.partner_id and lead.partner_id.id or False,
            'default_partner_ids': partner_ids,
            'default_section_id': lead.section_id and lead.section_id.id or False,
            'default_name': lead.name,
        }
        return res
    
    def _meeting_count_lead(self, cr, uid, ids, field_name, arg, context=None):
        Event = self.pool['calendar.event']
        return {
            lead_id: Event.search_count(cr,uid, [('lead_id', '=', lead_id)], context=context)
            for lead_id in ids
        }
        
    _columns = {
        'meeting_count_lead': fields.function(_meeting_count_lead, string='# Meetings', type='integer'),
    }
    
class calendar_event(osv.osv):
    """ Model for Calendar Event """
    _inherit = 'calendar.event'
        
    _columns = {
        'lead_id': fields.many2one('crm.lead', 'Lead', domain="[('type', '=', 'lead')]"),
    }
    
    def create(self, cr, uid, vals, context=None):
        res = super(calendar_event, self).create(cr, uid, vals, context=context)
        obj = self.browse(cr, uid, res, context=context)
        if obj.lead_id:
            self.pool.get('crm.lead').log_meeting(cr, uid, [obj.lead_id.id], obj.name, obj.start, obj.duration, context=context)
        return res
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: