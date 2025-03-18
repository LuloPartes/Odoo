# -*- coding: utf-8 -*-
{
    'name': "zue_autoparts_portal",

    'summary': """
        E-commerce Autopartes""",

    'description': """
        E-commerce Autopartes
    """,

    'author': "ZUE S.A.S.",
    'website': "www.zue.com.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'zue_autoparts', 'website', 'website_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/actions_shop.xml',
        'views/actions_product_product.xml',
        'views/actions_product_website.xml',
        'views/actions_ecommerce_product_settings.xml',
        'views/actions_filter_parameterization.xml',
        'views/menus.xml',
    ],
    # 'assets': {
    #     'web.assets_frontend': [
    #         'zue_autoparts_portal/static/src/css/magnifier_images.css',
    #         'zue_autoparts_portal/static/src/js/magnifier_images.js'
    #     ]
    # },
    'bootstrap': True,
    'license': 'LGPL-3',
}
