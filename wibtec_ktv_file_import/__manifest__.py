# -*- coding: utf-8 -*-
{
    'name': 'Wibtec K-TV (file import)',
    'version': '1.0',
    'summary': 'File import',
    'description': 'File import',
    'author': 'Wibtec',
    'company': 'Wibtec',
    'website': 'www.wibtec.com',
    'category': 'Accounting',
    'depends': [
                'account_invoicing'
                ],
    'data': [
            #'security/ir.model.access.csv',
            'data/ir_cron_data.xml',
            'views/file_import_view.xml',
            'views/ktv_view.xml',
            ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
