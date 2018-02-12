# -*- coding: utf-8 -*-
from openerp import models,fields,api

class stock_picking(models.Model):
    _inherit = 'stock.picking'
    od_notes = fields.Text(string="Notes")

# class stock_transfer_details(models.TransientModel):
#     _inherit = 'stock.transfer_details'
#     @api.one
#     def do_detailed_transfer(self):
#         res = super(stock_transfer_details,self).do_detailed_transfer()
#         context = self._context
#         active_id = context.get('active_id')
#         picking = self.env['stock.picking']
#         lot = self.env['stock.production.lot']
#         pick_obj = picking.browse(active_id)
#         partner_id = pick_obj.partner_id and pick_obj.partner_id.id
#         print "partner id>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",partner_id
#         for line in self.item_ids:
#             lot_id = line.lot_id and line.lot_id.id or False
#             if lot_id:
#                 lot_obj = lot.browse(lot_id)
#                 lot_obj.write({'od_partner_id':partner_id})
#         return res
