# -*- coding: utf-8 -*-
{
    'name': 'HR Automation - Job Requisition',
'version': '18.0.1.0.0',  
  'category': 'Human Resources',
    'summary': 'Manage job requisition requests and recruitment planning',
    'author': 'Ahmed Sameh',
    'license': 'LGPL-3',
    'depends': [
        'base'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/job_application.xml',
        'views/menu_items.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}