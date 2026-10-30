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
        'views/api_settings.xml',
        'views/ui_customization.xml',
        'demo/hr_automation_demo.xml',
        'views/menu_items.xml',
    ],
    'demo': [
        'demo/hr_automation_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hr_automation/static/src/scss/custom_styles.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
