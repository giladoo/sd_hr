# -*- coding: utf-8 -*-
{
    'name': 'SD HR',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': """ It works as base module for HR extended modules """,
    'author': 'Arash Homayounfar',
    'company': 'Giladoo',
    'maintainer': 'Giladoo',
    'website': "https://www.giladoo.com",
    'installable': True,
    'auto_install': False,
    'application': False,
    'depends': ['hr'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'assets': {
        'web.assets_backend':[
            'sd_hr/static/src/components/**/*'
        ],

    },
    'license': 'LGPL-3',
}
