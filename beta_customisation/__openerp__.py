# -*- coding: utf-8 -*-
{
    "name" : "Beta Customisation",
    "version" : "0.2",
    "author": "Aslam Up",
    "category" : "CRM",
    "description": """ Beta Customisations""",
    "website": "http://www.betait.net",
    "depends": ['base', 'crm', 'calendar', 'analytic','orchid_beta_project', 'orchid_cost_sheet', 'account', 'hr'],
    'data': [
            'crm/crm_lead_view.xml',
            'project/project_view.xml',
            'project/analytic_view.xml',
            'purchase/purchase_view.xml',
            'hr/hr_view.xml',
            'hr/job_view.xml'
            ],
    'demo': [],
    'installable': True,
  
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
