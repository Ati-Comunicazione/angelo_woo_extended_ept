# -*- coding: utf-8 -*-
{
    'name': 'Angelo Woo Extended Ept',

    'summary': """Scheduler to update price from Odoo to WooCommerce""",

    'description': """Scheduler to update price from Odoo to WooCommerce""",

    'author': 'Emipro Technologies Pvt. Ltd.',

    'website': 'http://www.emiprotechnologies.com',

    'maintainer': 'Emipro Technologies Pvt. Ltd.',

    'license': 'OPL-1',

    'category': 'Sales',

    'version': '0.1',

    'depends': ['woo_commerce_ept'],

    'data': [
        'wizard/cron_configuration_ept.xml',
        'data/ir_cron_data.xml',
        'wizard/res_config_view.xml',
    ],

    'installable': True,
    'auto_install': False,
}