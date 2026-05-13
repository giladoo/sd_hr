{
    'name': 'SD HR',
    'version': '18.0.1.0.3',
    'category': 'Human Resources',
    'summary': """ It works as base module for HR extended 1 modules """,
    'author': 'Arash Homayounfar',
    'company': 'Giladoo',
    'maintainer': 'Giladoo',
    'website': "https://www.giladoo.com/sdhr",
    'installable': True,
    'auto_install': False,
    'application': False,
    'depends': ['hr',],
	'external_dependencies': {
    	'python': ['python-docx',]
    },
    'data': [
        'security/ir.model.access.csv',


        # 'wizard/hr_panel_template.xml',
        # 'wizard/hr_panel.xml',
        'views/views.xml',
        'views/grading.xml',

        'views/cost_center.xml',
        'views/hr_work_place.xml',
        'views/hr_job_views.xml',
        'views/hr_employee_views.xml',
        'views/doc_template.xml',
        'views/variables_views.xml',
        'report/export_list.xml',
        'data/barcode_sequence.xml',
        'data/data_grading.xml',
        'data/variable_sequence.xml',
        'wizard/employee_import.xml',
    ],
    'assets':{
        'web.assets_backend':[
            'sd_hr/static/src/components/**/*',
            # 'sd_hr/static/src/lib/plain_tree/plain_tree.g002.css',
        ],
    },

    'license': 'LGPL-3',
}
# -*- coding: utf-8 -*-
