from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, float_round
import pandas as pd
import base64

class documents_mixin(models.AbstractModel):
    _inherit = 'documents.mixin'

    def _get_document_product(self):
        return self.env['product.template']

    def _get_document_vals(self, attachment):
        document_vals = super(documents_mixin, self)._get_document_vals(attachment)

        if self._check_create_documents():
            document_vals['product_id'] = self._get_document_product().id
        return document_vals

class documents_document(models.Model):
    _inherit = 'documents.document'

    product_id = fields.Many2one('product.template',string='Producto')

    @api.model_create_multi
    def create(self, values_list):
        for values in values_list:
            company = self.env.company
            if values.get('folder_id',0) == company.product_folder.id:
                values['product_id'] = values.get('partner_id',0)
                values['partner_id'] = 0
        return super(documents_document, self).create(values_list)

class account_move_line(models.Model):
    _inherit = 'account.move.line'

    z_quantity_refund = fields.Float(string='Cantidad Producto', compute='_compute_z_quantity_refund')
    z_price_subtotal_refund = fields.Float(string='Subtotal Producto', compute='_compute_z_price_subtotal_refund')

    @api.depends('quantity')
    def _compute_z_quantity_refund(self):
        for record in self:
            record.z_quantity_refund = abs(record.quantity)*-1 if record.move_id.move_type in ['out_refund','in_refund'] else record.quantity

    @api.depends('price_subtotal')
    def _compute_z_price_subtotal_refund(self):
        for record in self:
            record.z_price_subtotal_refund = abs(record.price_subtotal) * -1 if record.move_id.move_type in ['out_refund','in_refund'] else record.price_subtotal

class zue_attributes_product_autoparts(models.Model):
    _name = 'zue.attributes.product.autoparts'
    _description = 'Atributos del producto'
    _rec_name = 'z_rec_name'
    _order = 'z_sequence'

    z_product_id = fields.Many2one('product.template', string='Producto', ondelete='cascade', required=True)
    z_sequence = fields.Integer(string='Secuencia', readonly=True)
    z_type = fields.Selection([('1', 'Conectores'),
                               ('2', 'Protocolos'),
                               ('3', 'Sistema Eléctrico'),
                               ('4', 'Voltaje'),
                               ('100', 'Otro')], string="Tipo", required=True)
    z_attribute_setting_id = fields.Many2one('zue.settings.autoparts', string='Atributo', domain="[('z_type','=',z_type),('z_type','!=','100')]")
    z_value = fields.Char(string='Valor')
    z_rec_name = fields.Char('Descripción Atributo', compute='_get_z_rec_name')

    @api.depends('z_type', 'z_attribute_setting_id', 'z_value')
    def _get_z_rec_name(self):
        for record in self:
            if record.z_type != '100':
                name_type = dict(self._fields['z_type'].selection).get(record.z_type)
                name = record.z_attribute_setting_id.display_name if record.z_attribute_setting_id else name_type
            else:
                name = f'{record.z_attribute_setting_id.display_name} - {record.z_value or " "}'
            record.z_rec_name = name
    @api.model_create_multi
    def create(self, values_list):
        obj_create = super(zue_attributes_product_autoparts, self).create(values_list)
        obj_create._get_z_rec_name()

        return obj_create

class zue_market_research_x_product(models.Model):
    _name = 'zue.market.research.x.product'
    _description = 'Estudio de mercado por producto'

    z_product_template_id = fields.Many2one('product.template', string='Producto', required=True)
    z_market_research_id = fields.Many2one('zue.market.research', string='Estudio de mercado', required=True)
    z_market_value = fields.Float(related='z_market_research_id.z_value', string='Valor')

class product_template(models.Model):
    _inherit = 'product.template'
    _order = 'default_code,name'
    _rec_names_search = ['name', 'default_code','company_code','factory_code']

    # TRACK VISIBILITY OLD FIELDS
    name = fields.Char(tracking=True)
    sale_ok = fields.Boolean(tracking=True)
    purchase_ok = fields.Boolean(tracking=True)
    detailed_type = fields.Selection(tracking=True)
    uom_id = fields.Many2one(tracking=True)
    uom_po_id = fields.Many2one(tracking=True)
    list_price = fields.Monetary(tracking=True)
    standard_price = fields.Monetary(tracking=True)
    default_code = fields.Char(tracking=True)
    barcode = fields.Char(tracking=True)

    standard_price = fields.Float(store=True)
    # Vendedores
    z_sales_user_ids = fields.Many2many('res.users', string='Vendedores Comerciales')
    #Segmento
    class_id = fields.Many2one('stock.class', string='Familia')
    segments_id = fields.Many2one(related="class_id.segments_id", string='Sistema', store=True)
    subsegments_id = fields.Many2one(related="class_id.subsegments_id", string='División', store=True)
    #tariff_item_id = fields.Char(related="class_id.tariff_item", string='Partida arancelaria', store=True)
    #tariff_rate_id = fields.Float(related="class_id.tariff_rate", string='Porcentaje', store=True)
    z_attributes_product_ids = fields.One2many('zue.attributes.product.autoparts', 'z_product_id', string="Atributos")
    #Origen
    z_special_location_id = fields.Many2one('zue.special.locations', string='Ubicación')
    brands_id = fields.Many2one('stock.brands', string='Marca')
    source_id = fields.Many2one('res.country', string='Procedencia',domain=[('inventory_source', '=', True)])
    type_id = fields.Many2one('stock.type', string='Tipo Origen')

    #Destino
    vehicle_destination_ids = fields.One2many('vehicle.destination','product_template_ids', string='Destino')

    #Información general(Pestaña)
    factory_code = fields.Char(string="Código de Fábrica", tracking=True)
    company_code = fields.Char(string="Company code", tracking=True)
    z_short_article = fields.Char(string="OEM")

    #Documentos
    document_count = fields.Integer(compute='_compute_document_count')

    #Cantidad disponible
    z_qty_available = fields.Float('Cantidad disponible', compute='_compute_z_qty_available')
    z_qty_available_main_second = fields.Float('A la mano MP', compute='_compute_z_qty_available')

    # Lista de precios
    z_product_pricelist = fields.Text(compute='_compute_product_pricelist', string='Lista de precios')
    z_purchases_in_process = fields.Integer(string='Compras en proceso', compute='_compute_z_purchases_in_process')

    #Master del producto
    z_purchase_order_ids = fields.Many2many('purchase.order.line',string='Ordenes de compra del producto')
    z_account_move_ids = fields.Many2many('account.move.line', string='Facturas del producto')
    #z_return_warranties_ids = fields.Many2many('zue.returns.warranties.return.lines', string='Devoluciones del producto', compute='_compute_z_master_product')
    z_available_per_location = fields.Html(string='Disponible por Bodega', compute='_compute_available_per_location')

    #lista de precios
    z_market_research_ids = fields.One2many('zue.market.research.x.product','z_product_template_id', string='Estudio de mercado')

    def _compute_available_per_location(self):
        for record in self:
            text = ''
            obj_quant = self.env['stock.quant'].search([('product_id.product_tmpl_id', '=', record.id), ('location_id.z_stock_main', '=', True)])
            if obj_quant:
                text += '<p><b>Disponible por ubicación</b></p>'
                text += '<table class="table table-borderless table-sm">'
                for quants in obj_quant:
                    text += '<tr>'
                    text += '<td>' + quants.location_id.complete_name + ': </td>'
                    text += '<td align="right">' + str(int(quants.available_quantity)) + ' Unidades</td>'
                    text += '</tr>'

                text += '</table>'
                record.z_available_per_location = text
            else:
                record.z_available_per_location = ''

    # def action_product_tmpl_forecast_report(self):
    #     self.ensure_one()
    #     user_group = list(self.env['res.groups'].search([('name', 'ilike', 'Visibilidad Clientes - Asesor Comercial')], limit=1).get_external_id().values())[0]
    #
    #     if self.user_has_groups(user_group):
    #         res = self.env['zue.pivot.report.product.replenishment'].update_pivot_replenishment(product_id=self.id, tmpl_product=True)
    #
    #         if res:
    #             action = self.env["ir.actions.actions"]._for_xml_id("zue_autoparts.zue_action_zue_pivot_product_replenishment")
    #         else:
    #             raise ValidationError(_('No se encontró una previsión para este producto. Por favor verifique!'))
    #
    #     else:
    #         action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_replenishment_product_product_action")
    #
    #     return action

    def _compute_z_purchases_in_process(self):
        for record in self:
            total = 0
            obj_order_line = record.env['purchase.order.line'].search([('product_id.product_tmpl_id', '=', record.id),
                                                                       ('qty_invoiced', '=', 0),
                                                                       ('order_id.is_shipped', '=', False)])

            for line in obj_order_line:
                if not line.order_id.is_shipped:
                    total += line.product_qty

            record.z_purchases_in_process = total

    def _compute_z_qty_available(self):
        for record in self:
            obj_stock_quant = self.env['stock.quant'].search(['&', ('product_id.product_tmpl_id', '=', record.id), '|', ('location_id.z_stock_main', '=', True), ('location_id.z_stock_second', '=', True)])
            if len(obj_stock_quant) > 0:
                z_qty_available = 0
                z_qty_available_second = 0
                for quant in obj_stock_quant:
                    z_qty_available += quant.available_quantity if quant.location_id.z_stock_main else 0
                    z_qty_available_second += quant.available_quantity if quant.location_id.z_stock_second else 0

                record.z_qty_available = z_qty_available
                record.z_qty_available_main_second = z_qty_available + z_qty_available_second
            else:
                record.z_qty_available = 0
                record.z_qty_available_main_second = 0

    # def _compute_z_master_product(self):
    #     for record in self:
    #         user_group = list(self.env['res.groups'].search([('name', 'ilike', 'Visibilidad Clientes - Asesor Comercial')],limit=1).get_external_id().values())[0]
    #         obj_purchase_order_line = self.env['purchase.order.line'].search([('product_id.product_tmpl_id', '=', record.id)])
    #         if self.user_has_groups(user_group):
    #             obj_account_move_line = self.env['account.move.line'].search(
    #                 [('product_id.product_tmpl_id', '=', record.id),
    #                  ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
    #                  ('move_id.invoice_user_id', '=', self.env.user.id),
    #                  ('account_id.internal_group', '=', 'income')]) #Filtrar un solo movimiento
    #         else:
    #             obj_account_move_line = self.env['account.move.line'].search(
    #                 [('product_id.product_tmpl_id', '=', record.id),
    #                  ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
    #                  ('account_id.internal_group', '=', 'income')])
    #         #obj_zue_returns_warranties_return_lines = self.env['zue.returns.warranties.return.lines'].search([('z_product_id.product_tmpl_id','=',record.id)])
    #
    #         record.z_purchase_order_ids = obj_purchase_order_line.ids
    #         record.z_account_move_ids = obj_account_move_line.ids
    #         #record.z_return_warranties_ids = obj_zue_returns_warranties_return_lines.ids

    def action_open_zue_quants(self):
        domain = [('product_id', 'in', self.product_variant_ids.ids),('location_id.z_stock_main','=',True)]
        action = self.env['stock.quant'].action_view_inventory()
        action['domain'] = domain
        action["name"] = _('Update Quantity')
        return action

    def _get_document_product(self):
        return self

    def _get_product_template_domain(self):
        self.ensure_one()
        user_domain = [('product_id','=',self.id)]
        return user_domain

    def _compute_document_count(self):
        # Método no optimizado para lotes ya que sólo se utiliza en la vista de formulario.
        for product in self:
            if product.name:
                product.document_count = self.env['documents.document'].search_count(
                    product._get_product_template_domain())
            else:
                product.document_count = 0

    def action_open_documents(self):
        self.ensure_one()
        hr_folder = self._get_document_folder()
        action = self.env['ir.actions.act_window']._for_xml_id('documents.document_action')

        action['context'] = {
            'default_product_id': self.id,
            'default_partner_id': self.id,
            'searchpanel_default_folder_id': hr_folder and hr_folder.id,
        }
        action['domain'] = self._get_product_template_domain()
        return action

    @api.depends()
    def _compute_product_pricelist(self):
        for record in self:

            #self.env['product.pricelist.item'].search([('product_tmpl_id','=', record.id)])
            z_product_pricelist = ''
            obj_allproduct_list = self.env['product.pricelist.item'].search([('applied_on', '=', '3_global')])
            for list in sorted(obj_allproduct_list, key=lambda x: x.pricelist_id.sequence):
                all_continue = True
                obj_product_list_base = self.env['product.pricelist.item']
                if list.base_pricelist_id:
                    obj_global_base = list.base_pricelist_id.item_ids.filtered(lambda x: x.applied_on == '3_global')
                    obj_product_list_base = self.env['product.pricelist.item'].search([('pricelist_id','=',list.base_pricelist_id.id),('product_tmpl_id', '=', record.id)])
                    if len(obj_global_base) == 0 and len(obj_product_list_base) == 0:
                        all_continue = False
                if all_continue:
                    if len(obj_product_list_base) > 0:
                        price_product = list.pricelist_id._get_product_price(record, obj_product_list_base[0].min_quantity + 1, False)
                    else:
                        price_product = list.pricelist_id._get_product_price(record, list.min_quantity+1, False)
                    price_product = '{:,.2f}'.format(price_product)
                    price_product = ((price_product.replace(",","|")).replace(".", ",")).replace("|", ".")
                    min_quantity_product = '{:,.2f}'.format(list.min_quantity)
                    min_quantity_product = ((min_quantity_product.replace(",", "|")).replace(".", ",")).replace("|", ".")
                    if z_product_pricelist != '':
                        z_product_pricelist += f'\n » {list.pricelist_id.name} - Precio {list.pricelist_id.currency_id.symbol} {str(price_product)} | Cant. mínima {min_quantity_product}'
                    else:
                        z_product_pricelist += f' » {list.pricelist_id.name} - Precio {list.pricelist_id.currency_id.symbol} {str(price_product)} | Cant. mínima {min_quantity_product}'
            obj_product_list = self.env['product.pricelist.item'].search([('product_tmpl_id', '=', record.id)])
            for list in sorted(obj_product_list, key=lambda x: x.pricelist_id.sequence):
                min_quantity_product = '{:,.2f}'.format(list.min_quantity)
                min_quantity_product = ((min_quantity_product.replace(",", "|")).replace(".", ",")).replace("|", ".")
                if z_product_pricelist != '':
                    z_product_pricelist += f'\n » {list.pricelist_id.name} - Precio {list.price} | Cant. mínima {min_quantity_product}'
                else:
                    z_product_pricelist += f' » {list.pricelist_id.name} - Precio {list.price} | Cant. mínima {min_quantity_product}'
            record.z_product_pricelist = z_product_pricelist

    # @api.onchange('class_id')
    # def _compute_available_attributes_ids(self):
    #     for record in self:
    #         record.z_attributes_product_ids = [(5, 0, 0)]
    #         if record.class_id:
    #             lst_available_type = []
    #             obj_available_attributes = self.env['zue.attributes.autoparts'].search(
    #                 [('id', 'in', record.class_id.z_attributes_ids.ids)])
    #             for aa in obj_available_attributes:
    #                 lst_available_type.append((0, 0, {'z_sequence': aa.z_sequence,
    #                                                   'z_type': aa.z_type,
    #                                                   'z_attribute_setting_id': aa.z_attribute_setting_id.id if aa.z_attribute_setting_id else False}))
    #             if len(lst_available_type) > 0:
    #                 record.z_attributes_product_ids = lst_available_type

    # @api.model_create_multi
    # def create(self, values_list):
    #     for values in values_list:
    #         create_attributes = False
    #         if values.get('class_id', False) and not values.get('z_attributes_product_ids', False):
    #             create_attributes = True
    #     result = super(product_template, self).create(values_list)
    #     if create_attributes:
    #         result._compute_available_attributes_ids()
    #     return result

class product_product(models.Model):
    _inherit = 'product.product'
    _order = 'default_code,name'
    _rec_names_search = ['name', 'default_code','company_code','factory_code']

    factory_code = fields.Char(related='product_tmpl_id.factory_code',string="Código de Fábrica", store=True)
    company_code = fields.Char(related='product_tmpl_id.company_code',string="Código Compañia", store=True)

    # Segmento
    class_id = fields.Many2one(related='product_tmpl_id.class_id', string='Familia', store=True)
    segments_id = fields.Many2one(related="product_tmpl_id.segments_id", string='Sistema', store=True)
    subsegments_id = fields.Many2one(related="product_tmpl_id.subsegments_id", string='División', store=True)
    #tariff_item_id = fields.Char(related="product_tmpl_id.tariff_item_id", string='Partida arancelaria', store=True)
    #tariff_rate_id = fields.Float(related="product_tmpl_id.tariff_rate_id", string='Porcentaje', store=True)
    z_special_locations_id = fields.Many2one(related='product_tmpl_id.z_special_location_id', string='Ubicaciones')
    z_product_pricelist = fields.Text(related='product_tmpl_id.z_product_pricelist', string='Lista de precios')
    z_qty_available = fields.Float(related='product_tmpl_id.z_qty_available', string='Cantidad disponible')
    z_qty_available_main_second = fields.Float(related='product_tmpl_id.z_qty_available_main_second', string='A la mano MP')

    # Origen
    brands_id = fields.Many2one(related='product_tmpl_id.brands_id', string='Marca', store=True)
    source_id = fields.Many2one(related='product_tmpl_id.source_id', string='Procedencia', store=True)
    type_id = fields.Many2one(related='product_tmpl_id.type_id', string='Tipo Origen', store=True)
    z_purchases_in_process = fields.Integer(string='Compras en proceso', related='product_tmpl_id.z_purchases_in_process')

    # def action_product_forecast_report(self):
    #     self.ensure_one()
    #     user_group = list(self.env['res.groups'].search([('name', 'ilike', 'Visibilidad Clientes - Asesor Comercial')], limit=1).get_external_id().values())[0]
    #
    #     if self.user_has_groups(user_group):
    #         res = self.env['zue.pivot.report.product.replenishment'].update_pivot_replenishment(product_id=self.id)
    #
    #         if res:
    #             action = self.env["ir.actions.actions"]._for_xml_id("zue_autoparts.zue_action_zue_pivot_product_replenishment")
    #         else:
    #             raise ValidationError(_('No se encontró una previsión para este producto. Por favor verifique!'))
    #
    #     else:
    #         action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_replenishment_product_product_action")
    #
    #     return action


class vehicle_destination(models.Model):
    _name = 'vehicle.destination'
    _description = 'Destino Vehiculo'

    product_template_ids = fields.Many2one('product.template',string="Producto")
    vehicle_brand_id = fields.Many2one('fleet.vehicle.model.brand', string="Marca")
    vehicle_type = fields.Selection(related="vehicle_line_id.vehicle_type", string='Tipo de vehículo')
    vehicle_line_id = fields.Many2one('fleet.vehicle.model', string="Línea", domain="[('brand_id','=',vehicle_brand_id)]")
    z_vehicle_specifications_id = fields.Many2one('zue.vehicle.specifications', string="Especificación")
    initial_year = fields.Integer(string="Año inicial")
    final_year = fields.Integer(string="Año final")

    @api.constrains('initial_year','final_year')
    def _validation_year(self):
        for record in self:
            if record.initial_year < 1950 or record.initial_year > 2050:
                raise UserError(_('El destino no esta dentro de los años disponibles (1950 a 2050)'))
            if record.final_year < 1950 or record.final_year > 2050:
                raise UserError(_('El destino no esta dentro de los años disponibles (1950 a 2050)'))

class stock_location(models.Model):
    _inherit = 'stock.location'

    z_stock_main = fields.Boolean(string='¿Es una bodega principal?')
    z_stock_second = fields.Boolean(string='¿Es una bodega secundaria?')
    z_stock_warehouse = fields.Boolean(string='¿Es una bodega de stock?')
    z_stock_input = fields.Boolean(string='¿Es una bodega de input?')
    z_stock_inv_resume = fields.Boolean(string='Resumen de inventario')

class stock_quant(models.Model):
    _inherit = "stock.quant"

    #z_class_id = fields.Many2one(related='product_id.product_tmpl_id.class_id', string='Familia', store=True)
    z_segments_id = fields.Many2one(related="product_id.product_tmpl_id.segments_id", string='Sistema', store=True)
    z_subsegments_id = fields.Many2one(related="product_id.product_tmpl_id.subsegments_id", string='División', store=True)
    z_brands_id = fields.Many2one(related='product_id.product_tmpl_id.brands_id', string='Marca', store=True)

class product_pricelist(models.Model):
    _inherit = 'product.pricelist'

    z_restrict_advisors = fields.Boolean(string='Restringir para asesores comerciales')

class product_packaging(models.Model):
    _inherit = 'product.packaging'

    active = fields.Boolean(string='Activo', default=True)

# class ReplenishmentReport(models.AbstractModel):
#     _inherit = 'report.stock.report_product_product_replenishment'
#
#     def _get_report_data(self, product_template_ids=False, product_variant_ids=False):
#         assert product_template_ids or product_variant_ids
#         res = {}
#
#         if self.env.context.get('warehouse'):
#             warehouse = self.env['stock.warehouse'].browse(self.env.context.get('warehouse'))
#         else:
#             warehouse = self.env['stock.warehouse'].browse(self.get_warehouses()[0]['id'])
#
#         wh_location_ids = [loc['id'] for loc in self.env['stock.location'].search_read(
#             [('id', 'child_of', warehouse.view_location_id.id)],
#             ['id'],
#         )]
#
#         # Get the products we're working, fill the rendering context with some of their attributes.
#         if product_template_ids:
#             product_templates = self.env['product.template'].browse(product_template_ids)
#             res['product_templates'] = product_templates
#             res['product_variants'] = product_templates.product_variant_ids
#             res['multiple_product'] = len(product_templates.product_variant_ids) > 1
#             res['uom'] = product_templates[:1].uom_id.display_name
#             res['quantity_on_hand'] = sum(product_templates.mapped('qty_available'))
#             res['virtual_available'] = sum(product_templates.mapped('virtual_available'))
#             res['purchase_in_process'] = sum(product_templates.mapped('z_purchases_in_process'))
#             res['qty_available_main_second'] = sum(product_templates.mapped('z_qty_available_main_second'))
#         elif product_variant_ids:
#             product_variants = self.env['product.product'].browse(product_variant_ids)
#             res['product_templates'] = False
#             res['product_variants'] = product_variants
#             res['multiple_product'] = len(product_variants) > 1
#             res['uom'] = product_variants[:1].uom_id.display_name
#             res['quantity_on_hand'] = sum(product_variants.mapped('qty_available'))
#             res['virtual_available'] = sum(product_variants.mapped('virtual_available'))
#             res['purchase_in_process'] = sum(product_variants.mapped('z_purchases_in_process'))
#             res['qty_available_main_second'] = sum(product_variants.mapped('z_qty_available_main_second'))
#         res.update(self._compute_draft_quantity_count(product_template_ids, product_variant_ids, wh_location_ids))
#
#         res['lines'] = self._get_report_lines(product_template_ids, product_variant_ids, wh_location_ids)
#         return res


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _get_aggregated_product_quantities(self, **kwargs):
        aggregated_move_lines = super()._get_aggregated_product_quantities(**kwargs)
        for aggregated_move_line in aggregated_move_lines:
            product_name = aggregated_move_lines[aggregated_move_line]['product'].product_tmpl_id.name
            product_default_code = aggregated_move_lines[aggregated_move_line]['product'].product_tmpl_id.default_code
            product_company_code = aggregated_move_lines[aggregated_move_line]['product'].product_tmpl_id.company_code
            aggregated_move_lines[aggregated_move_line]['product_default_code'] = product_default_code
            aggregated_move_lines[aggregated_move_line]['product_company_code'] = product_company_code
            aggregated_move_lines[aggregated_move_line]['name'] = product_name
            aggregated_move_lines[aggregated_move_line]['description'] = False
        return aggregated_move_lines

