# -*- coding: utf-8 -*-
{
    "name" : "Beta Invoice",
    "version" : "0.1",
    "author": "Jamshid K",
    "category" : "Account Invoice",
    "description": """ Invoice Customization""",
    "website": "http://www.betait.net",
    "depends": ['account','orchid_cost_sheet','orchid_cost_centre'],
    'data': [
            'security/ir.model.access.csv',
            'account/invoice_view.xml',
            'models/transfer_acc_view.xml',
             'models/replace_acc_view.xml',
#             'wizard/transfer.xml',
            ], 
    'demo': [],
    'installable': True,
  
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
