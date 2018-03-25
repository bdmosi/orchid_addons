# -*- coding: utf-8 -*-
from openerp import fields,models,api,_
from openerp.exceptions import Warning
import xlwt
from cStringIO import StringIO
import base64

 
 
class EmployeeKPIReport(models.TransientModel):
    _name = 'employee.kpi.report'
    template_id = fields.Many2one('audit.template',string="Audit Template")
    month =fields.Selection([('01','January'), ('02','February'), ('03','March'), ('04','April'), ('05','May'), ('06','June'),
                                  ('07','July'), ('08','August'), ('09','September'), ('10','October'), ('11','November'), ('12','December')], string='Month',required=True)
    excel_file=fields.Binary('Dowload Report Excel',readonly=True)
    file_name = fields.Char('Excel File', size=64,readonly=True)
     
     
     
    def _get_data(self,month,template_id):
        employee_pool = self.env['hr.employee']
        domain = []
        if template_id:
            domain += [('audit_temp_id','=',template_id)]
        employee_data = employee_pool.search(domain) 
        month_number = int(month)
        emp_data = [{'Product':x.product_id.name,'Description':x.product_id.description_sale or 'No Description','Quantity':x.qty,'Inventory Value':x.inventory_value,'Cost':x.inventory_value/x.qty,'Location':x.location_id.name} for x in quant_data_set]
        return quant_data
    @api.multi
    def print_excel_report(self):
        location_id = self.location_id and self.location_id.id or False
        result = self._get_data(location_id)
        dataframe= pd.DataFrame(result,columns=['Product','Description','Quantity','Cost','Inventory Value','Location'])
        filename ='stocklist.xlsx'
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        fp = StringIO()
        writer.book.filename = fp
        dataframe.to_excel(writer, sheet_name='Sheet1')
        writer.save()
        excel_file = base64.encodestring(fp.getvalue())
        self.write({'excel_file':excel_file,'file_name':filename})
        fp.close()
        return {
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'wiz.od.stock.list',
              'res_id': self.id,
              'type': 'ir.actions.act_window',
              'target': 'new'
              }
     
