# -*- coding: utf-8 -*-
{
    'name': "zue_autoparts",
    'icon': '/zue_autoparts/static/description/icon.png',
    'summary': """
        Proyecto para ajustes personalizados de Autopartes""",

    'description': """
        Proyecto para ajustes personalizados de Autopartes
    """,

    'author': "ZUE S.A.S.",
    'website': "www.zue.com.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    "version": "17.0.1.0.0",

    # any module necessary for this one to work correctly
    'depends': ['base','timer','stock','fleet','crm','sale','purchase','l10n_co_reports','documents','documents_product', 'account','website_sale','sale_product_configurator','account_accountant','account_followup','point_of_sale','pos_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/products_stock.xml',
        'views/parameters_fleet.xml',
        'views/general_parameters_stock.xml',
        'views/actions_special_locations.xml',
        'views/menus.xml',
    ],
    'license': 'LGPL-3',
}
