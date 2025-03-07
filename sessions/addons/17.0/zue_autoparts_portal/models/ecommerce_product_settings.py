# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class zue_ecommerce_product_settings(models.Model):
    _name = 'zue.ecommerce.product.settings'
    _description = 'Configuración vista producto en el ecommerce'

    z_company_id = fields.Many2one('res.company', string='Compañía', readonly=True, required=True, default=lambda self: self.env.company)
    z_field_show_ids = fields.One2many('zue.ecommerce.product.settings.fields','z_ecommerce_setting_id',string='Campos a mostrar')
    z_show_alternative_products = fields.Boolean('Mostrar productos alternativos')
    z_show_optional_products = fields.Boolean('Mostrar productos opcionales')

    _sql_constraints = [('zue_ecommerce_product_settings_uniq', 'unique(z_company_id)',
                         'Ya existe configuración para esta compañía, por favor verificar.')]

class zue_ecommerce_product_settings_fields(models.Model):
    _name = 'zue.ecommerce.product.settings.fields'
    _description = 'Configuración vista producto en el ecommerce campos a mostrar'

    z_ecommerce_setting_id = fields.Many2one('zue.ecommerce.product.settings', string='Configuración', required=True)
    z_sequence = fields.Integer(string='Orden')
    z_field_show_id = fields.Many2one('ir.model.fields',
                                    domain="[('model', '=', 'product.template'),('ttype', 'not in', ['many2many','one2many','text','binary'])]",
                                    ondelete="cascade", string='Campos a mostrar', required=True)

class product_template(models.Model):
    _inherit = 'product.template'

    def load_ecommerce_product_settings(self):
        return self.env['zue.ecommerce.product.settings'].search([('z_company_id','=',self.env.company.id)])

    def get_value_field_ecommerce(self,field):
        try:
            val_field = self[field].display_name
        except:
            val_field = self[field]

        return val_field

