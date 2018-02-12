# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _



class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    _columns = {
        'so_line_id':fields.many2one('sale.order.line','Sale Order Line')
    }

class od_generate_purchase_order_line(osv.osv_memory):
    _inherit = 'od.orchid_so2po.generate_purchase_order_line'
    _columns = {
        'so_line_id':fields.many2one('sale.order.line','Sale Order Line'),
        'od_analytic_acc_id':fields.many2one('account.analytic.account','Analytic Account'),
    }

class generate_purchase_order(osv.osv_memory):
    _inherit = 'orchid_so2po.generate_purchase_order'

    def default_get(self, cr, uid, fields, context=None):
        res = super(generate_purchase_order, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        active_id = context and  context.get('active_id')
        vals = []
        if active_id:
            sale_order_obj = self.pool.get('sale.order').browse(cr, uid, active_id, context=context)
            res.update({'purchase_requsition_id': sale_order_obj.od_purchase_requsition_id.id or False})
            for line in sale_order_obj.order_line:
                vals.append({'so_line_id':line.id,'product_id':line.product_id.id,'name':line.name,'product_qty':line.product_uom_qty,'product_uom_id':line.product_uom.id,'od_analytic_acc_id':line.od_analytic_acc_id and line.od_analytic_acc_id.id or False })
            res.update({'od_purchase_generate_line': vals})
        return res
class sale_order(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    
    def get_cost_from_costsheet(self,cr,uid,product_id,cost_sheet_id):
        matline_pool=self.pool.get('od.cost.mat.main.pro.line')
        mat_id=matline_pool.search(cr,uid,[('part_no','=',product_id),('cost_sheet_id','=',cost_sheet_id)],limit=1)
        mat_obj =matline_pool.browse(cr,uid,mat_id)
        return mat_obj.discounted_unit_supplier_currency or 0.0
    def get_cost_from_sale_order_line(self,cr,uid,product_id,order_id):
        sale_order_line =  self.pool.get('sale.order.line')
        sale_order_line_id = sale_order_line.search(cr,uid,[('product_id','=',product_id),('order_id','=',order_id)],limit=1)
        sale_lin_ob = sale_order_line.browse(cr,uid,sale_order_line_id)
        return sale_lin_ob.od_sup_unit_cost or 0.0
    
    def generate_purchase_order(self, cr, uid, ids, supplier_id, pricelist_id, warehouse_id, wizard,copy_desc, context=None):
        purchase_obj = self.pool.get('purchase.order')
        purchase_line_obj = self.pool.get('purchase.order.line')
        warehouse_obj = self.pool.get('stock.warehouse')
        purchase_requsition_obj = self.pool.get('purchase.requisition')
        purchase_requsition_line_obj = self.pool.get('purchase.requisition.line')
        warehouse = warehouse_obj.browse(cr, uid, warehouse_id, context=context)
        if not warehouse:
            return False
        if isinstance(warehouse, list):
            warehouse = warehouse[0]
        self_order = self.browse(cr,uid,ids,context=context)[0]
        date_order = self_order and self_order.date_order
        sale_order = self_order and self_order.name
        order_id = self_order and self_order.id
        od_cost_sheet_id = self_order.od_cost_sheet_id and self_order.od_cost_sheet_id.id
        od_cost_centre_id = self_order.od_cost_centre_id and self_order.od_cost_centre_id.id 
        od_branch_id = self_order.od_branch_id and self_order.od_branch_id.id 
        od_division_id = self_order.od_division_id and self_order.od_division_id.id
        project_id = self_order.project_id and self_order.project_id.id 
        purchase_requsition_id = wizard.purchase_requsition_id and wizard.purchase_requsition_id.id
        if not purchase_requsition_id:
            for order in self.browse(cr, uid, ids, context=context):
                vals = {}
                line_vals = {}
                vals['origin'] = order.name
                vals['exclusive'] = 'multiple'
                purchase_requsition_id = purchase_requsition_obj.create(cr, uid, vals, context=context)
                for line in order.order_line:
                    line_vals['product_id'] = line.product_id and line.product_id.id
                    line_vals['product_qty'] = line.product_uom_qty
                    line_vals['requisition_id'] = purchase_requsition_id
                    purchase_requsition_line_obj.create(cr, uid, line_vals, context=context)
            self.write(cr,uid,ids,{'od_purchase_requsition_id':purchase_requsition_id})
        purchase_line_vals = {}
        for purchase in wizard:
            vals = purchase_obj.onchange_partner_id(cr, uid, [], supplier_id)['value']
            currency_id= self.pool.get('product.pricelist').browse(cr, uid, purchase.pricelist_id.id, context=context).currency_id.id
            picking_type_id = purchase_obj._get_picking_in(cr,uid,context=context)
            onchange_pick_type = purchase_obj.onchange_picking_type_id(cr,uid,[],picking_type_id,context)['value']
            vals.update(onchange_pick_type)
            vals['origin'] = sale_order
            vals['partner_id'] = purchase.partner_id.id
            vals['pricelist_id'] = purchase.pricelist_id.id
            vals['currency_id'] = currency_id
            vals['warehouse_id'] = purchase.warehouse_id.id
            vals['picking_type_id'] = picking_type_id
            vals['requisition_id'] = purchase_requsition_id
            vals['date_order'] = date_order
            vals['od_cost_sheet_id'] = od_cost_sheet_id 
            vals['od_cost_centre_id'] = od_cost_centre_id
            vals['od_branch_id'] = od_branch_id 
            vals['od_division_id'] = od_division_id
            vals['project_id'] = project_id
             
            purchase_id = purchase_obj.create(cr, uid, vals, context=context)
            for ob in wizard.od_purchase_generate_line:
                purchase_line_vals = purchase_line_obj.onchange_product_id(cr, uid, ids, pricelist_id, ob.product_id.id,
                                                ob.product_qty, ob.product_uom_id.id, supplier_id,context=context)['value']
                product_id  = ob.product_id and ob.product_id.id
#                 cost = self.get_cost_from_costsheet(cr,uid,product_id,cost_sheet_id)
                cost = self.get_cost_from_sale_order_line(cr,uid,product_id, order_id)
                purchase_line_vals['product_id'] = product_id
                if not (product_id or copy_desc):
                    raise Warning('Either You should Tick Copy Description or You should Select Product in Product Line')
                
                purchase_line_vals['price_unit'] = cost
                purchase_line_vals['product_uom'] = ob.product_uom_id.id
                purchase_line_vals['product_uom_qty'] = ob.product_qty
                purchase_line_vals['order_id'] = purchase_id
                purchase_line_vals['so_line_id'] = ob.so_line_id.id
                purchase_line_vals['account_analytic_id'] = ob.od_analytic_acc_id and ob.od_analytic_acc_id.id
                if not (ob.product_id and ob.product_id.id):
                    purchase_line_vals['date_planned'] = date_order
                purchase_line_vals['od_gross'] = cost
                if copy_desc:
                    purchase_line_vals['name'] = ob.name
                purchase_line_obj.create(cr, uid, purchase_line_vals, context=context)
        return True
