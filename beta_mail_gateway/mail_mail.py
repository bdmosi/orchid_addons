# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    ThinkOpen Solutions Brasil
#    Copyright (C) Thinkopen Solutions <http://www.tkobr.com>.
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

from openerp.addons.base.ir.ir_mail_server import extract_rfc2822_addresses
from openerp.osv import osv, fields
import random as rd


class mail_mail(osv.Model):
    _inherit = 'mail.mail'

    def send(self, cr, uid, ids, auto_commit=False, raise_exception=False, context=None):
        for email in self.pool.get('mail.mail').browse(cr, uid, ids, context=context):
            from_rfc2822 = extract_rfc2822_addresses(email.email_from)[-1]
            server_ids = self.pool.get('ir.mail_server').search(cr, uid, [('sequence','<',11)],
                                                      context=context)
            print "server ids>>>>>>>>>>>>>>>>>>>>>",server_ids
            server_id = rd.choice(server_ids)
            print "server id>>>>>>>>>>>>>>>>>",server_id
            if server_id:
                self.write(cr, uid, ids, {'mail_server_id': server_id,
                                          'reply_to': email.email_from, },
                           context=context)
        return super(mail_mail, self).send(cr, uid, ids, auto_commit=auto_commit, raise_exception=raise_exception,
                                           context=context)
