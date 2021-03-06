# -*- coding: utf-8 -*-
##############################################################################
from datetime import datetime, timedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _


class product_category(osv.osv):
    _inherit = 'product.category'
    _columns = {
                'od_timesheet':fields.boolean('Timesheet'),
                'od_trading':fields.boolean('Trading'),
                'od_expense':fields.boolean('Expense'),
                }

class od_product_group(osv.osv):
    _name = 'od.product.group'
    _description = 'od.product.group'
    _columns = {
        'name': fields.char('Name',size=128,required="1"),
        'code': fields.char('Code',size=10),
        'description': fields.text('Description'),
    }
    _sql_constraints = [
                        ('name_uniq', 'unique(name)', 'Name must be unique...!'),
                        ]


class od_product_sub_group(osv.osv):
    _name = 'od.product.sub.group'
    _description = 'od.product.sub.group'
    _columns = {
        'name': fields.char('Name',size=128,required="1"),
        'code': fields.char('Code',size=10),
        'parent_group_id':fields.many2one('od.product.group','Parent Group'),
        'description': fields.text('Description'),
    }
    _sql_constraints = [
                       ('name_uniq', 'unique(name)', 'Name must be unique...!'),
                        ]

                        
class od_product_type(osv.osv):
    _name = 'od.product.type'
    _description = 'od.product.type'
    _columns = {
        'name': fields.char('Name',size=128,required="1"),
        'code': fields.char('Code',size=10),
        'description': fields.text('Description'),
    }
    _sql_constraints = [
                       ('name_uniq', 'unique(name)', 'Name must be unique...!'),
                        ]


class od_product_sub_type(osv.osv):
    _name = 'od.product.sub.type'
    _description = 'od.product.sub.type'
    _columns = {
        'name': fields.char('Name',size=128,required="1"),
        'parent_type_id':fields.many2one('od.product.type','Parent Type',),
        'code': fields.char('Code',size=10),
        'description': fields.text('Description'),
    }
    _sql_constraints = [
                       ('name_uniq', 'unique(name)', 'Name must be unique...!'),
                        ]

class od_product_classification(osv.osv):
    _name = 'od.product.classification'
    _description = 'od.product.classification'
    _columns = {
        'name': fields.char('Name',size=128,required="1"),
        'code': fields.char('Code',size=10),
        'description': fields.text('Description'),
    }
    _sql_constraints = [
                       ('name_uniq', 'unique(name)', 'Name must be unique...!'),
                        ]


class od_product_brand(osv.osv):
    _name = 'od.product.brand'
    _description = 'od.product.brand'
    _columns = {
        'name': fields.char('Name',size=128,required="1"),
        'code': fields.char('Code',size=10),
        'description': fields.text('Description'),
    }
    _sql_constraints = [
                       ('name_uniq', 'unique(name)', 'Name must be unique...!'),
                        ]


class od_product_hscode(osv.osv):
    _name = 'od.product.hscode'
    _description = 'od.product.hscode'
    _columns = {
        'name': fields.char('Name',size=128,required="1"),
#        'code': fields.char('Code',size=10),
        'customs_duty_percentage':fields.float('Customs Duty(%)'),
        'description': fields.text('Description'),
    }
    _sql_constraints = [
                        ('name_uniq', 'unique(name)', 'Name must be unique...!'),
                        ]



class product_template(osv.osv):
    _inherit = "product.template"
    _columns = {
        'od_company_id': fields.many2many('res.company','od_res_odcompany_product_rel','od_product_id','od_company_id','Companies'),
        'od_pdt_group_id': fields.many2one('od.product.group','Group'),

        'od_pdt_sub_group_id': fields.many2one('od.product.sub.group','Sub Group'),
        'od_pdt_type_id': fields.many2one('od.product.type','Type'),
        'od_pdt_sub_type_id': fields.many2one('od.product.sub.type','Sub Type'),
        'od_pdt_classification_id': fields.many2one('od.product.classification','Classification'),

        'od_pdt_brand_id': fields.many2one('od.product.brand','Brand'),
        'od_pdt_hscode_id': fields.many2one('od.product.hscode','HS Code'),
        'od_timesheet':fields.boolean('Timesheet'),
        'od_trading':fields.boolean('Trading'),
        'od_expense':fields.boolean('Expense'),
#         'od_bar_qty':fields.integer('Barcode Qty')
    }

class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
        'od_product_id': fields.many2many('product.template','od_res_odcompany_product_rel','od_company_id','od_product_id')
    }
    
