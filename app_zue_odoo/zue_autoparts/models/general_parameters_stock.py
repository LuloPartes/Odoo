from odoo import models, fields, api, _
from collections import defaultdict
from odoo.tools import add, float_compare, frozendict, split_every
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class stock_segments(models.Model):
    _name = 'stock.segments'
    _description = 'Segmentos inventario'

    code = fields.Integer(string='Código', required=True)
    name = fields.Char(string='Descripción', required=True)
    z_publish_ecommerce = fields.Boolean(string='Publicar en E-commerce', default=True)

    _sql_constraints = [
        ('stock_segments_uniq', 'UNIQUE (code)',
         'El código digitado ya se encuentra en uso, por favor verifique')
    ]

class stock_subsegments(models.Model):
    _name = 'stock.subsegments'
    _description = 'SubSegmentos inventario'

    segments_id = fields.Many2one('stock.segments', string='Sistema', required=True)
    code = fields.Integer(string='Código', required=True)
    name = fields.Char(string='Descripción', required=True)
    is_starter = fields.Boolean(string='Es Arranque o Alternador')

    _sql_constraints = [
        ('stock_subsegments_uniq', 'UNIQUE (segments_id,code)',
         'El código digitado ya se encuentra en uso para este Sistema, por favor verifique')
    ]

class stock_class(models.Model):
    _name = 'stock.class'
    _description = 'Clases inventario'

    segments_id = fields.Many2one('stock.segments', string='Sistema', required=True)
    subsegments_id = fields.Many2one('stock.subsegments', string='División', required=True, domain="[('segments_id','=',segments_id)]")
    class_code = fields.Integer(string='Código clase', required=True)
    tariff_id = fields.Many2one('zue.tariffs.imports', string='Arancel')
    tariff_item = fields.Char(related="tariff_id.z_code", string='Partida arancelaria', store=True)
    tariff_rate = fields.Float(related="tariff_id.z_porc", string='Tarifa arancelaria', store=True)
    name = fields.Char(string='Descripción', required=True)
    z_attributes_ids = fields.One2many('zue.attributes.autoparts','z_class_id', string="Atributos")
    z_image = fields.Binary(string='Imagen')

    _sql_constraints = [
        ('stock_class_uniq', 'UNIQUE (segments_id,subsegments_id,class_code)',
         'El código digitado ya se encuentra en uso para este sistema y division, por favor verifique')
    ]

    @api.depends('name','segments_id','subsegments_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = "{} | Sistema: {} | División: {}".format(record.name, record.segments_id.name, record.subsegments_id.name)

class stock_type(models.Model):
    _name = 'stock.type'
    _description = 'Tipos de inventario'

    code = fields.Integer(string='Código', required=True)
    name = fields.Char(string='Descripción', required=True)

    _sql_constraints = [
        ('stock_type_uniq', 'UNIQUE (code)',
         'El código digitado ya se encuentra en uso, por favor verifique')
    ]

class stock_brands(models.Model):
    _name = 'stock.brands'
    _description = 'Marcas inventario'

    code = fields.Integer(string='Código', required=True)
    name = fields.Char(string='Descripción', required=True)
    image_1920 = fields.Image(string='Logo')
    type_order = fields.Selection([('a-z', 'Alfabética '), ('code', 'Código')], string='Orden catálogo',
                                  default='a-z', required=True)
    z_is_exclusive = fields.Boolean(string="Exclusiva")

    _sql_constraints = [
        ('stock_brands_uniq', 'UNIQUE (code)',
         'El código digitado ya se encuentra en uso, por favor verifique')
    ]

class zue_attributes_autoparts(models.Model):
    _name = 'zue.attributes.autoparts'
    _description = 'Atributos de autopartes'
    _rec_name = 'z_rec_name'
    _order = 'z_sequence'

    z_sequence = fields.Integer(string='Secuencia')
    z_class_id = fields.Many2one('stock.class', string='Familia', required=True)
    z_type = fields.Selection([('1', 'Conectores'),
                               ('2', 'Protocolos'),
                               ('3', 'Sistema Eléctrico'),
                               ('4', 'Voltaje'),
                               ('100', 'Otro')], string="Tipo", required=True)
    z_attribute_setting_id = fields.Many2one('zue.settings.autoparts', string='Atributo OTRO', domain="[('z_type','=',z_type)]")
    z_rec_name = fields.Char('Atributo', compute='_get_z_rec_name')

    # @api.depends('z_type','z_attribute_setting_id')
    # def _get_z_rec_name(self):
    #     for record in self:
    #         if record.z_type != '100':
    #             name = dict(self._fields['z_type'].selection).get(record.z_type)
    #         else:
    #             name = record.z_attribute_setting_id.display_name
    #         record.z_rec_name = name
    #
    # @api.model_create_multi
    # def create(self, values_list):
    #     res = super(zue_attributes_autoparts, self).create(values_list)
    #     for record in res:
    #         obj_products = self.env['product.template'].search([('class_id', '=', res.z_class_id.id)])
    #         lst_available_type = []
    #         lst_available_type.append((0, 0, {'z_sequence': record.z_sequence,
    #                                           'z_type': record.z_type,
    #                                           'z_attribute_setting_id': record.z_attribute_setting_id.id if record.z_attribute_setting_id else False}))
    #         if len(lst_available_type) > 0:
    #             for product in obj_products:
    #                 product.z_attributes_product_ids = lst_available_type
    #     return res
    #
    # def write(self, vals):
    #     res = super(zue_attributes_autoparts, self).write(vals)
    #     for record in self:
    #         obj_products = self.env['product.template'].search([('class_id', '=', record.z_class_id.id)])
    #         for product in obj_products:
    #             for attributes in product.z_attributes_product_ids:
    #                 if (attributes.z_type == record.z_type and record.z_type != '100') or (record.z_type == '100' and attributes.z_attribute_setting_id.id == record.z_attribute_setting_id.id):
    #                     attributes.write({'z_sequence':record.z_sequence})
    #     return res
    #
    # def unlink(self):
    #     for record in self:
    #         obj_products = self.env['product.template'].search([('class_id','=',record.z_class_id.id)])
    #         for product in obj_products:
    #             for attributes in product.z_attributes_product_ids:
    #                 if (attributes.z_type == record.z_type and record.z_type != '100') or (record.z_type == '100' and attributes.z_attribute_setting_id.id == record.z_attribute_setting_id.id):
    #                     attributes.unlink()
    #     return super(zue_attributes_autoparts, self).unlink()

class zue_settings_autoparts(models.Model):
    _name = 'zue.settings.autoparts'
    _description = 'Configuración atributos autopartes'

    z_type = fields.Selection([('1', 'Conectores'),
                               ('2', 'Protocolos'),
                               ('3', 'Sistema Eléctrico'),
                               ('4', 'Voltaje'),
                               ('100', 'Otro')], string="Tipo", required=True)
    z_name = fields.Char(string="Nombre")
    z_value = fields.Char(string='Descripción')
    z_identifier = fields.Char(string='Identificador')

    @api.depends('z_type','z_identifier','z_value','z_name')
    def _compute_display_name(self):
        for record in self:
            if record.z_type != '100':
                name = dict(self._fields['z_type'].selection).get(record.z_type)
                if record.z_identifier != record.z_value:
                    name += f' | {record.z_identifier}-{record.z_value}'
                else:
                    name += f' | {record.z_identifier}'
            else:
                name = record.z_name
            record.display_name = name

class zue_market_research(models.Model):
    _name = 'zue.market.research'
    _description = 'Estudio de mercado'

    z_supplier_name = fields.Char(string='Nombre proveedor', required=True)
    z_market_code = fields.Char(string='Codigo mercado', required=True)
    z_value = fields.Float(string='Valor', required=True)
    z_equivalences = fields.Char(string='Equivalencias')
    z_supplier_description = fields.Char(string='Descripción proveedor')

    @api.depends('z_supplier_name','z_market_code')
    def _compute_display_name(self):
        for record in self:
            record.display_name = "Proveedor: {} | Codigo mercado: {}".format(record.z_supplier_name, record.z_market_code)

class res_country(models.Model):
    _inherit = 'res.country'

    inventory_source = fields.Boolean(string='Procedencia de inventario')


