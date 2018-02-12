from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import except_orm, Warning, RedirectWarning

import base64
import xlwt
from cStringIO import StringIO
from pprint import pprint
import logging
from openerp import tools
_logger = logging.getLogger(__name__)

# from openerp.osv import orm, fields
from datetime import datetime
# from cStringIO import StringIO
# import base64
# import xlwt
import time
from datetime import date
from datetime import datetime,date
from datetime import timedelta
# from pprint import pprint
# import logging
# from openerp import tools
# _logger = logging.getLogger(__name__)

# from openerp.exceptions import except_orm







class OrchidVatRegisterInput(models.TransientModel):
	"""
	Orchid Tax Register Input.
	"""
	_name = 'orchid.vat.register.input'
	_description = 'Tax Register Input'

	from_date = fields.Date(string='From Date')
	to_date = fields.Date(string='To Date')
	wizard_line=fields.One2many('orchid.vat.register.input.line','wizard_line_id',string='line_id_')
	excel_file = fields.Binary(string='Dowload Report Excel',readonly="1")
	file_name = fields.Char(string='Excel File',readonly="1")


	def print_pdf(self, cr, uid, ids, context=None):
		data={}

		if context is None:
			context={}
		# print 'kkkkkkkkkkkkkkkk',self.read(cr, uid, ids,['from_date','to_date','wizard_line'],context)
		
		data = self.read(cr, uid, ids,['from_date','to_date','wizard_line'])[0]

		from_date=data.get('from_date')
		to_date=data.get('to_date')

		# a=self.pool['account.relation'].browse(cr,uid,'account_id',context=context) 
		wizard_line_account_id=[]

		for acc_lines in self.browse(cr, uid, ids, context=context):
			for acc_line in acc_lines.wizard_line:
				wizard_line_account_id.append(acc_line.account_id.id)
		print wizard_line_account_id

		if from_date>to_date:
			raise Warning("From Date cannot be greater than To Date!!")

		inv_obj = self.pool['account.move.line']
		inv_datas  =inv_obj.search(cr,uid,[('account_id','in',wizard_line_account_id),('date','>',from_date),('date','<',to_date)])
		# print"qqqqq",inv_datas



		obj_ls=[]
		for res in inv_obj.browse(cr, uid, inv_datas,context=context):
			# if inv_obj.search(cr,uid,[('journal_id.type','=','purchase')]):
			if res.journal_id and res.journal_id.type=='purchase':
				
				obj_ls.append(res)
		# print 'listttttt',obj_ls
		vat_period=datetime.strptime(data.get('from_date'), '%Y-%m-%d').strftime('%d/%m/%Y')+"\tto\t"+datetime.strptime(data.get('to_date'), '%Y-%m-%d').strftime('%d/%m/%Y')
		print 'vat-periodddddd',vat_period
		
		
		report_date = date.today()
		report_date=report_date.strftime("%d/%m/%Y")
		print 'report_date',report_date

		

		




		
		local_purchase=0
		foreign_purchase=0
		total_credit=0
		total_debit=0
		trans_d=0
		trans_c=0
		all_lines = []
		for ls in obj_ls:
			for record in ls:
				data = {}
				flag=0
				data['doc_num']=record.move_id.name
				data['description']=ls.name
				# print 'descr',data['description']
				data['doc_type']=record.journal_id.name
				data['doc_date']=record.date
				data['debit']=record.debit
				data['credit']=record.credit
				data['currency']=ls.company_id.currency_id.name
				# print 'cnnnn',data['currency']
				data['tax_code']=record.account_id.name
				data['trans_type']=ls.invoice.od_order_type_id.name
				# print 'ccccccc',data['trans_type']


				if data['trans_type']=='Local Purchase':
					trans_d=trans_d+data['debit']
					trans_c=trans_c+data['credit']
					local_purchase=trans_c-trans_d

				if data['trans_type']=='Foreign Purchase':
					trans_d=trans_d+data['debit']
					trans_c=trans_c+data['credit']
					foreign_purchase=trans_c-trans_d

				if data['trans_type']==0:
					flag=1
				# print 'recorddddddddd',data
				data['doc_date']=datetime.strptime(data['doc_date'], '%Y-%m-%d').strftime('%d/%m/%Y')

				# print 'dateeeeeeeee',data['doc_date']
				total_credit=total_credit+data['credit']
				# print 'creeeeeeeeee',total_credit
				total_debit=total_debit+data['debit']
				all_lines.append(data)
		move_lines = {'filter': {'from': from_date, 'to': to_date}, 'period': {'vat_period': vat_period}, 'total': {'total_credit': total_credit,'total_debit':total_debit},
					'transaction_type': {'local_purchase': local_purchase,'foreign_purchase':foreign_purchase},'datas': {'values': all_lines}}	
		# print "lineeeeeeeeeeeeeeeeeeeeeeeeeeeeeessssssssssssssssssssssssssssssssssssss",move_lines
		return self.pool['report'].get_action(cr,uid,[], 'orchid_beta_vat.report_vatregister_pdf',context=context, data=move_lines)


	def generate(self, cr, uid, ids, context=None):
		data={}

		if context is None:
			context={}
		# print 'kkkkkkkkkkkkkkkk',self.read(cr, uid, ids,['from_date','to_date','wizard_line'],context)
		
		data = self.read(cr, uid, ids,['from_date','to_date','wizard_line'])[0]

		from_date=data.get('from_date')
		to_date=data.get('to_date')

		# a=self.pool['account.relation'].browse(cr,uid,'account_id',context=context) 
		wizard_line_account_id=[]

		for acc_lines in self.browse(cr, uid, ids, context=context):
			for acc_line in acc_lines.wizard_line:
				wizard_line_account_id.append(acc_line.account_id.id)
		print wizard_line_account_id

		if from_date>to_date:
			raise Warning("From Date cannot be greater than To Date!!")

		inv_obj = self.pool['account.move.line']
		inv_datas  =inv_obj.search(cr,uid,[('account_id','in',wizard_line_account_id),('date','>',from_date),('date','<',to_date)])
		print"qqqqq",inv_datas



		obj_ls=[]
		for res in inv_obj.browse(cr, uid, inv_datas,context=context):
			# if inv_obj.search(cr,uid,[('journal_id.type','=','purchase')]):
			if res.journal_id and res.journal_id.type=='purchase':
				
				obj_ls.append(res)
		# print 'listttttt',obj_ls

		return self.generate_excel(cr,uid,ids,data,obj_ls,inv_datas,context=None)




	def generate_excel(self,cr,uid,ids,data,obj_ls,inv_datas,context=None):

		vat_period=datetime.strptime(data.get('from_date'), '%Y-%m-%d').strftime('%d/%m/%Y')+"\tto\t"+datetime.strptime(data.get('to_date'), '%Y-%m-%d').strftime('%d/%m/%Y')
		print 'vat-periodddddd',vat_period
		
		
		report_date = date.today()
		report_date=report_date.strftime("%d/%m/%Y")
		print 'report_date',report_date

		

		# partner_obj = self.env['res.company'].browse('partner_id')
		# partner_name = partner_obj.name
		# print 'sssssssssssssssssss',partner_name


		print 'rrrrrrrrrrrrrrrrrrrrrrrrrrr' 
		workbook= xlwt.Workbook(encoding="UTF-8")

		#For coloured cells
		xlwt.add_palette_colour("custom_colour", 0x10)
		workbook.set_colour_RGB(0x10,178, 190, 181)

		filename='InputVat.xls'
		sheet= workbook.add_sheet('Input VAT Report',cell_overwrite_ok=True)
		
		style_coloured = xlwt.easyxf('font:name calibri,height 200;align: horiz center, vert center;pattern: fore_colour custom_colour,pattern solid;borders:top_color black, bottom_color black, right_color black, left_color black, top thin,right thin,bottom thin,left thin;pattern: fore_colour custom_colour,pattern solid')
		style_title= xlwt.easyxf('font:name calibri,height 200;align: horiz left, vert center;')
		style_left= xlwt.easyxf('font:name calibri,height 200;align: horiz left, vert center;borders:top_color black, bottom_color black, right_color black, left_color black, top thin,right thin,bottom thin,left thin;')
		style_right=xlwt.easyxf('font:name calibri,height 200;align: horiz right, vert center;borders:top_color black, bottom_color black, right_color black, left_color black, top thin,right thin,bottom thin,left thin;')
		style_centre=xlwt.easyxf('align: horiz center, vert center;')
		style_filter=xlwt.easyxf('font:name calibri,height 200;align: horiz center, vert center;borders:top_color black, bottom_color black,top thin,bottom thin;pattern: fore_colour custom_colour,pattern solid')
		style_grey=xlwt.easyxf('pattern:fore_colour custom_colour,pattern solid')

		row = 0
		col =0

		title=['Input VAT','Report Date','Period from']

		sheet.write(row,col,title[0],style_title)
		col=8
		sheet.write(row,col,title[1],style_title)
		col=col+1
		sheet.write(row,col,report_date,style_left)
		col=0
		row=row+1	
		sheet.write(row,col,title[2],style_title)
		col=col+1
		sheet.write(row,col,vat_period,style_left)



		row=row+1
		col=0
		header=['Document Number','Description','Document Type','Document Date','Posting Date'
				,'Debit','Credit','Local Currency','Transaction Type','Tax Code']

		for i in range(0,10):
			sheet.write(row,col,header[i],style_coloured)
			col=col+1

		print "ttttttttttttttttttttttttttttttttttttttt"

	
		# partner_obj=[]
		# for i in self.pool['res.company'].browse(cr,uid,ids,context=context):
		# 	partner_obj.append(i)

		# print 'sssssssssssssssssss',partner_obj

		# partner = self.pool['res.company'].browse(cr,uid,ids,context=context)
		# print partner.currency_id






		
		# obj = self.pool['account.move.line']

		row=row+1
		
		local_purchase=0
		foreign_purchase=0
		total_credit=0
		total_debit=0
		trans_d=0
		trans_c=0
		for ls in obj_ls:
			for record in ls:
				data = {}
				flag=0
				data['doc_num']=record.move_id.name
				data['description']=ls.name
				# print 'descr',data['description']
				data['doc_type']=record.journal_id.name
				data['doc_date']=record.date
				data['debit']=record.debit
				data['credit']=record.credit
				data['currency']=ls.company_id.currency_id.name
				# print 'cnnnn',data['currency']
				data['tax_code']=record.account_id.name
				data['trans_type']=ls.invoice.od_order_type_id.name
				# print 'ccccccc',data['trans_type']


				if data['trans_type']=='Local Purchase':
					trans_d=trans_d+data['debit']
					trans_c=trans_c+data['credit']
					local_purchase=trans_c-trans_d

				if data['trans_type']=='Foreign Purchase':
					trans_d=trans_d+data['debit']
					trans_c=trans_c+data['credit']
					foreign_purchase=trans_c-trans_d

				if data['trans_type']==0:
					flag=1
				# print 'recorddddddddd',data
				data['doc_date']=datetime.strptime(data['doc_date'], '%Y-%m-%d').strftime('%d/%m/%Y')

				# print 'dateeeeeeeee',data['doc_date']
				total_credit=total_credit+data['credit']
				# print 'creeeeeeeeee',total_credit
				total_debit=total_debit+data['debit']



				
				col=0
				sheet.write(row,col,data['doc_num'],style_right)
				col=col+1
				sheet.write(row,col,data['description'],style_left)
				col=col+1
				sheet.write(row,col,data['doc_type'],style_left)
				col=col+1
				sheet.write(row,col,data['doc_date'],style_right)
				col=col+1
				sheet.write(row,col,data['doc_date'],style_right)
				col=col+1
				sheet.write(row,col,data['debit'],style_right)
				col=col+1
				
				sheet.write(row,col,data['credit'],style_right)
				# print 'ooooooooo'
				col=col+1
				sheet.write(row,col,data['currency'],style_left)
				col=col+1

				if flag==1:
					# print 'mmmmmmmmmmm'
					sheet.write(row,col,"",style_left)
				else:
					# print 'nnnnnnnnnn'
					sheet.write(row,col,data['trans_type'],style_left)

				col=col+1
				sheet.write(row,col,data['tax_code'],style_left)
				row=row+1
		
		col=0	
		footer=['Total','Net Input VAT Recoverable','Local purchases','Foreign Purchases']

			
		sheet.write(row,col,footer[0],style_coloured)

		for col in range(1,5):
			sheet.write(row,col,"",style_coloured)

		col=5
		sheet.write(row,col,total_debit,style_coloured)
		col=col+1
		sheet.write(row,col,total_credit,style_coloured)

		for col in range(7,10):
			sheet.write(row,col,"",style_coloured)

		row=row+1
		col=0
		for col in range(0,5):
			sheet.write(row,col,"",style_filter)

		col=2
		sheet.write(row,col,footer[1],style_filter)

		col=5
		sheet.write(row,col,"",style_coloured)

		col=5
		payable=total_credit-total_debit
		sheet.write(row,col,payable,style_coloured)

		col=2
		row=row+1
		footer_row=row
		sheet.write(row,col,footer[2],style_centre)
		row=row+1
		sheet.write(row,col,footer[3],style_centre)
		# row=row+1
		# sheet.write(row,col,footer[4],style_centre)
		row=footer_row
		col=5
		sheet.write(row,col,local_purchase,style_right)
		row=row+1
		sheet.write(row,col,foreign_purchase,style_right)
		# row=row+1
		# sheet.write(row,col,footer[2],style_centre)

		



		fp = StringIO()
		workbook.save(fp)
		excel_file = base64.encodestring(fp.getvalue())
		self.write(cr,uid,ids,{'excel_file':excel_file,'file_name':filename})
		fp.close()
		return {
			  'view_type': 'form',
			  "view_mode": 'form',
			  'res_model': 'orchid.vat.register.input',
			  'res_id': ids[0],
			  'type': 'ir.actions.act_window',
			  'target': 'new'
			  }






class OrchidVatRegisterOutput(models.TransientModel):
	"""
	Orchid Tax Register Output.
	"""
	_name = 'orchid.vat.register.output'
	_description = 'Tax Register Output'

	from_date = fields.Date(string='From Date')
	to_date = fields.Date(string='To Date')
	wizard_line=fields.One2many('orchid.vat.register.output.line','wizard_line_id',string='line_id_')
	excel_file = fields.Binary(string='Dowload Report Excel',readonly="1")
	file_name = fields.Char(string='Excel File',readonly="1")

	def print_pdf(self, cr, uid, ids, context=None):
		data={}

		if context is None:
			context={}
		
		data = self.read(cr, uid, ids,['from_date','to_date','wizard_line'])[0]
		from_date=data.get('from_date')
		to_date=data.get('to_date')

		wizard_line_account_id=[]
		# print 'iddddddd',wizard_line_account_id
		for acc_lines in self.browse(cr, uid, ids, context=context):
			for acc_line in acc_lines.wizard_line:
				wizard_line_account_id.append(acc_line.account_id.id)
		print wizard_line_account_id

		if from_date>to_date:
			raise Warning("From Date cannot be greater than To Date!!")

		inv_obj = self.pool['account.move.line']
		inv_datas  =inv_obj.search(cr,uid,[('account_id','in',wizard_line_account_id),('date','>',from_date),('date','<',to_date)])
		# print"qqqqq",inv_datas

		obj_ls=[]
		for res in inv_obj.browse(cr, uid, inv_datas,context=context):
			if res.journal_id and res.journal_id.type=='sale':
				# print 'ifffffffffffff',res
				obj_ls.append(res)

		# print 'listttttt',obj_ls
		vat_period=datetime.strptime(data.get('from_date'), '%Y-%m-%d').strftime('%d/%m/%Y')+"\tto\t"+datetime.strptime(data.get('to_date'), '%Y-%m-%d').strftime('%d/%m/%Y')
		print 'vat-periodddddd',vat_period
		

		report_date = date.today()
		report_date=report_date.strftime("%d/%m/%Y")
		print 'report_date',report_date
		total_credit=0
		total_debit=0
		all_lines = []
		for ls in obj_ls:
			for record in ls:
				data = {}
				flag=0
				data['doc_num']=record.move_id.name
				data['description']=ls.name
				data['doc_type']=record.journal_id.name
				data['doc_date']=record.date
				data['debit']=ls.debit
				data['credit']=ls.credit
				data['currency']=ls.company_id.currency_id.name
				
				data['trans_type']=ls.invoice.od_order_type_id.name
				print 'ccccccc',data['trans_type']
				data['tax_code']=record.account_id.name
				# print 'aaaaaaaaa',data['tax_code']
				# print 'recorddddddddd',data
				if data['trans_type']==0:
					flag=1


				data['doc_date']=datetime.strptime(data['doc_date'], '%Y-%m-%d').strftime('%d/%m/%Y')

				# print 'dateeeeeeeee',data['doc_date']
				total_credit=total_credit+data['credit']
				# print 'creeeeeeeeee',total_credit
				total_debit=total_debit+data['debit']
				all_lines.append(data)
		move_lines = {'filter': {'from': from_date, 'to': to_date}, 'period': {'vat_period': vat_period}, 'total': {'total_credit': total_credit,'total_debit':total_debit},
					'datas': {'values': all_lines}}	
		print "all_linesssssssssssssssssssssssssssssssssss",all_lines
		print "lineeeeeeeeeeeeeeeeeeeeeeeeeeeeeessssssssssssssssssssssssssssssssssssss",move_lines
		return self.pool['report'].get_action(cr,uid,[], 'orchid_beta_vat.report_vat_outputregister_pdf',context=context, data=move_lines)
		
		
	def generate(self, cr, uid, ids, context=None):
		data={}

		if context is None:
			context={}
		
		data = self.read(cr, uid, ids,['from_date','to_date','wizard_line'])[0]
		from_date=data.get('from_date')
		to_date=data.get('to_date')

		wizard_line_account_id=[]
		# print 'iddddddd',wizard_line_account_id
		for acc_lines in self.browse(cr, uid, ids, context=context):
			for acc_line in acc_lines.wizard_line:
				wizard_line_account_id.append(acc_line.account_id.id)
		print wizard_line_account_id

		if from_date>to_date:
			raise Warning("From Date cannot be greater than To Date!!")

		inv_obj = self.pool['account.move.line']
		inv_datas  =inv_obj.search(cr,uid,[('account_id','in',wizard_line_account_id),('date','>',from_date),('date','<',to_date)])
		# print"qqqqq",inv_datas

		obj_ls=[]
		for res in inv_obj.browse(cr, uid, inv_datas,context=context):
			if res.journal_id and res.journal_id.type=='sale':
				# print 'ifffffffffffff',res
				obj_ls.append(res)

		# print 'listttttt',obj_ls
		return self.generate_excel(cr,uid,ids,data,obj_ls,inv_datas,context=None)




	def generate_excel(self,cr,uid,ids,data,obj_ls,inv_datas,context=None):


		vat_period=datetime.strptime(data.get('from_date'), '%Y-%m-%d').strftime('%d/%m/%Y')+"\tto\t"+datetime.strptime(data.get('to_date'), '%Y-%m-%d').strftime('%d/%m/%Y')
		print 'vat-periodddddd',vat_period
		

		report_date = date.today()
		report_date=report_date.strftime("%d/%m/%Y")
		print 'report_date',report_date

		print 'rrrrrrrrrrrrrrrrrrrrrrrrrrr' 
		workbook= xlwt.Workbook(encoding="UTF-8")

		#For coloured cells
		xlwt.add_palette_colour("custom_colour", 0x10)
		workbook.set_colour_RGB(0x10,178, 190, 181)

		filename='OutputVat.xls'
		sheet= workbook.add_sheet('Output VAT Report',cell_overwrite_ok=True)
		
		style_coloured = xlwt.easyxf('font:name calibri,height 200;align: horiz center, vert center;pattern: fore_colour custom_colour,pattern solid;borders:top_color black, bottom_color black, right_color black, left_color black, top thin,right thin,bottom thin,left thin;pattern: fore_colour custom_colour,pattern solid')
		style_title= xlwt.easyxf('font:name calibri,height 200;align: horiz left, vert center;')
		style_left= xlwt.easyxf('font:name calibri,height 200;align: horiz left, vert center;borders:top_color black, bottom_color black, right_color black, left_color black, top thin,right thin,bottom thin,left thin;')
		style_right=xlwt.easyxf('font:name calibri,height 200;align: horiz right, vert center;borders:top_color black, bottom_color black, right_color black, left_color black, top thin,right thin,bottom thin,left thin;')
		style_centre=xlwt.easyxf('align: horiz center, vert center;')
		style_filter=xlwt.easyxf('font:name calibri,height 200;align: horiz center, vert center;borders:top_color black, bottom_color black,top thin,bottom thin;pattern: fore_colour custom_colour,pattern solid')
		style_grey=xlwt.easyxf('pattern:fore_colour custom_colour,pattern solid')
		row = 0
		col =0

		title=['Input VAT','Report Date','Period from']

		

		sheet.write(row,col,title[0],style_title)
		col=8
		sheet.write(row,col,title[1],style_title)
		col=col+1
		sheet.write(row,col,report_date,style_left)
		col=0
		row=row+1	
		sheet.write(row,col,title[2],style_title)
		col=col+1
		sheet.write(row,col,vat_period,style_left)

		row=row+1
		col=0
		header=['Document Number','Description','Document Type','Document Date','Posting Date'
				,'Debit','Credit','Local Currency','Transaction Type','Tax Code']

		for i in range(0,10):
			sheet.write(row,col,header[i],style_coloured)
			col=col+1
		
		print 'dataaaaaaaaaaaaaaaaaaaa'
		row=row+1
		total_credit=0
		total_debit=0
		for ls in obj_ls:
			for record in ls:
				data = {}
				flag=0
				data['doc_num']=record.move_id.name
				data['description']=ls.name
				data['doc_type']=record.journal_id.name
				data['doc_date']=record.date
				data['debit']=ls.debit
				data['credit']=ls.credit
				data['currency']=ls.company_id.currency_id.name
				
				data['trans_type']=ls.invoice.od_order_type_id.name
				print 'ccccccc',data['trans_type']
				data['tax_code']=record.account_id.name
				# print 'aaaaaaaaa',data['tax_code']
				# print 'recorddddddddd',data
				if data['trans_type']==0:
					flag=1


				data['doc_date']=datetime.strptime(data['doc_date'], '%Y-%m-%d').strftime('%d/%m/%Y')

				# print 'dateeeeeeeee',data['doc_date']
				total_credit=total_credit+data['credit']
				# print 'creeeeeeeeee',total_credit
				total_debit=total_debit+data['debit']

				# print 'creeeeeeeeee',total_debit




				
				col=0
				sheet.write(row,col,data['doc_num'],style_right)
				col=col+1
				sheet.write(row,col,data['description'],style_left)
				col=col+1
				sheet.write(row,col,data['doc_type'],style_left)
				col=col+1
				sheet.write(row,col,data['doc_date'],style_right)
				col=col+1
				sheet.write(row,col,data['doc_date'],style_right)
				col=col+1
				sheet.write(row,col,data['debit'],style_right)
				col=col+1
				
				sheet.write(row,col,data['credit'],style_right)
				col=col+1
				sheet.write(row,col,data['currency'],style_left)
				col=col+1
				if flag==1:
					sheet.write(row,col,"",style_left)
				else:
					sheet.write(row,col,data['trans_type'],style_left)
				col=col+1
				sheet.write(row,col,data['tax_code'],style_left)
				row=row+1
		
		
	
	
		col=0		
		footer=['Total','Net Output Payable']

		sheet.write(row,col,footer[0],style_coloured)

		for col in range(1,5):
			sheet.write(row,col,"",style_coloured)

		col=5
		sheet.write(row,col,total_debit,style_coloured)
		col=col+1
		sheet.write(row,col,total_credit,style_coloured)

		for col in range(7,10):
			sheet.write(row,col,"",style_coloured)

		row=row+1
		col=0
		for col in range(0,5):
			sheet.write(row,col,"",style_filter)
		col=2
		sheet.write(row,col,footer[1],style_filter)
		col=5
		payable=total_debit-total_credit
		sheet.write(row,col,payable,style_coloured)
		
			
			
				

		fp = StringIO()
		workbook.save(fp)
		excel_file = base64.encodestring(fp.getvalue())
		self.write(cr,uid,ids,{'excel_file':excel_file,'file_name':filename})
		fp.close()
		return {
			  'view_type': 'form',
			  "view_mode": 'form',
			  'res_model': 'orchid.vat.register.output',
			  'res_id': ids[0],
			  'type': 'ir.actions.act_window',
			  'target': 'new'
			  }







class OrchidVatRegisterInputLine(models.TransientModel):

	_name="orchid.vat.register.input.line"
	_description="orchid.vat.register.input.line"


	wizard_line_id=fields.Many2one("orchid.vat.register.input",string="accounts_line")
	account_id=fields.Many2one('account.account',string="ACCOUNTS")




class OrchidVatRegisterOutputLine(models.TransientModel):

	_name="orchid.vat.register.output.line"
	_description="orchid.vat.register.input.line"


	wizard_line_id=fields.Many2one("orchid.vat.register.output",string="accounts_line")
	account_id=fields.Many2one('account.account',string="ACCOUNTS")


class Report_input_pdf(models.AbstractModel):
	_name = 'report.orchid_beta_vat.report_vatregister_pdf'

	@api.multi
	def render_html(self, data=None):
		model = self.env.context.get('active_model')
		docs = self.env[model].browse(self.env.context.get('active_id'))
		report_date = date.today()
		report_date=report_date.strftime("%d/%m/%Y")
		# move_lines = {'filter': {'from': from_date, 'to': to_date}, 'period': {'vat_period': vat_period}, 'total': {'total_credit': total_credit,'total_debit':total_debit},
		# 			'transaction_type': {'local_purchase': local_purchase,'foreign_purchase':foreign_purchase},'datas': {'values': all_lines}}	
		# print "bbbbbbbbbbbbbbbbbbbbbbbbbbbbb",data['datas']['values']
		print "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",data
		report_obj = self.env['report']
		report = report_obj._get_report_from_name('orchid_beta_vat.report_vatregister_pdf')
		docargs = {
			'doc_ids': self.ids,
			'doc_model': model,
			'docs': docs,
			'lines': data['datas']['values'],
			'report_date': report_date,
			'vat_period': data['period']['vat_period'],
			'local_purchase' : data['transaction_type']['local_purchase'],
			'foreign_purchase' : data['transaction_type']['foreign_purchase'],
			'total_credit' : data['total']['total_credit'],
			'total_debit' : data['total']['total_debit'],
			}
		return report_obj.render('orchid_beta_vat.report_vatregister_pdf', docargs)

class Report_ouput_pdf(models.AbstractModel):
	_name = 'report.orchid_beta_vat.report_vat_outputregister_pdf'

	@api.multi
	def render_html(self, data=None):
		model = self.env.context.get('active_model')
		docs = self.env[model].browse(self.env.context.get('active_id'))
		report_date = date.today()
		report_date=report_date.strftime("%d/%m/%Y")
		# print "bbbbbbbbbbbbbbbbbbbbbbbbbbbbb",data['datas']['values']
		print "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",data
		report_obj = self.env['report']
		report = report_obj._get_report_from_name('orchid_beta_vat.report_vat_outputregister_pdf')
		docargs = {
			'doc_ids': self.ids,
			'doc_model': model,
			'docs': docs,
			'lines': data['datas']['values'],
			'report_date': report_date,
			'vat_period': data['period']['vat_period'],
			'total_credit' : data['total']['total_credit'],
			'total_debit' : data['total']['total_debit'],
			}
		return report_obj.render('orchid_beta_vat.report_vat_outputregister_pdf', docargs)						