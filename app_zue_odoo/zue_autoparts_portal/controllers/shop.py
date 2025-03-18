# -*- coding: utf-8 -*-
from odoo.http import request, route, Controller
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.main import QueryURL, Website
from odoo.tools import html_escape
from odoo.osv import expression
import datetime

class AutopartsShopPortal(WebsiteSale):

    def _shop_lookup_products(self, attrib_set, options, post, search, website):
        if request.website.env.context.get('zue_shop_args',False):
            options['zue_shop_args'] = request.website.env.context.get('zue_shop_args',False)
        return super(AutopartsShopPortal, self)._shop_lookup_products(attrib_set, options, post, search, website)

    @route()
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        request.website = request.website.with_context(zue_shop_args=request.httprequest.args)
        response = super(AutopartsShopPortal, self).shop(page=page, category=category, search=search,
                                                           min_price=min_price, max_price=max_price, ppg=ppg, **post)
        #Obtener filtros seleccionados
        selected_brands = [int(x) for x in request.httprequest.args.getlist('brand') if int(x) != 0]
        selected_vehicletype = [int(x) for x in request.httprequest.args.getlist('vehicletype') if int(x) != 0]
        selected_stock_vehicletype = [int(x) for x in request.httprequest.args.getlist('stock_vehicletype') if int(x) != 0]
        selected_vechicleyear = [int(x) for x in request.httprequest.args.getlist('vehicleyear') if int(x) != 0]
        selected_vechiclemodel = [int(x) for x in request.httprequest.args.getlist('vechiclemodel') if int(x) != 0]
        selected_vehicle_specifications = [int(x) for x in request.httprequest.args.getlist('vehiclespecifications') if int(x) != 0]
        selected_system = [int(x) for x in request.httprequest.args.getlist('system') if int(x) != 0]
        selected_division = [int(x) for x in request.httprequest.args.getlist('division') if int(x) != 0]
        selected_family = [int(x) for x in request.httprequest.args.getlist('family') if int(x) != 0]
        selected_brandsvehicle = [int(x) for x in request.httprequest.args.getlist('brandvehicle') if int(x) != 0]
        selected_conectores = [int(x) for x in request.httprequest.args.getlist('conectores') if int(x) != 0]
        selected_protocolos = [int(x) for x in request.httprequest.args.getlist('protocolos') if int(x) != 0]
        selected_sistemaelec = [int(x) for x in request.httprequest.args.getlist('sistemaelec') if int(x) != 0]
        selected_voltaje = [int(x) for x in request.httprequest.args.getlist('voltaje') if int(x) != 0]
        selected_autoparts_otros = [x for x in request.httprequest.args.getlist('autoparts_otros') if int(x) != 0]
        selected_attributes = selected_conectores+selected_protocolos+selected_sistemaelec+selected_voltaje+selected_autoparts_otros
        selected_fleet_aspimotor = [int(x) for x in request.httprequest.args.getlist('fleet_aspimotor') if int(x) != 0]
        selected_fleet_cabezamotor = [int(x) for x in request.httprequest.args.getlist('fleet_cabezamotor') if int(x) != 0]
        selected_fleet_carroceria = [int(x) for x in request.httprequest.args.getlist('fleet_carroceria') if int(x) != 0]
        selected_fleet_combustible = [int(x) for x in request.httprequest.args.getlist('fleet_combustible') if int(x) != 0]
        selected_fleet_nivelemisiones = [int(x) for x in request.httprequest.args.getlist('fleet_nivelemisiones') if int(x) != 0]
        selected_fleet_transmision = [int(x) for x in request.httprequest.args.getlist('fleet_transmision') if int(x) != 0]
        selected_fleet_traccion = [int(x) for x in request.httprequest.args.getlist('fleet_traccion') if int(x) != 0]
        selected_fleet_tipofreno = [int(x) for x in request.httprequest.args.getlist('fleet_tipofreno') if int(x) != 0]
        selected_fleet_tipovehiculo = [int(x) for x in request.httprequest.args.getlist('fleet_tipovehiculo') if int(x) != 0]
        selected_fleet_otros = [x for x in request.httprequest.args.getlist('fleet_otros') if int(x) != 0]
        selected_attributes_fleet = selected_fleet_aspimotor+selected_fleet_cabezamotor+selected_fleet_carroceria+selected_fleet_combustible+selected_fleet_nivelemisiones+selected_fleet_transmision+selected_fleet_traccion+selected_fleet_tipofreno+selected_fleet_tipovehiculo+selected_fleet_otros
        # Obtener información constante
        obj_brands = request.env['stock.brands'].sudo().search([])
        obj_brands_vehicle = request.env['fleet.vehicle.model.brand'].sudo().search([])
        domain_brands_vehicle = []
        if len(selected_brandsvehicle) > 0:
            domain_brands_vehicle.append(('brand_id', 'in', selected_brandsvehicle))
        obj_vehicle_model = request.env['fleet.vehicle.model'].sudo().search(domain_brands_vehicle)
        obj_segments = request.env['stock.segments'].sudo().search([('z_publish_ecommerce','=',True)])
        domain_subsegment = [('segments_id.z_publish_ecommerce','=',True)]
        domain_class = [('segments_id.z_publish_ecommerce','=',True)]
        if len(selected_system) > 0:
            domain_subsegment.append(('segments_id', 'in', selected_system))
            domain_class.append(('segments_id', 'in', selected_system))
        obj_subsegments = request.env['stock.subsegments'].sudo().search(domain_subsegment)
        if len(selected_division) > 0:
            domain_class.append(('subsegments_id', 'in', selected_division))
        obj_class = request.env['stock.class'].sudo().search(domain_class)
        domain_vehicle_specifications = []
        if len(selected_vechiclemodel) > 0:
            domain_vehicle_specifications.append(('z_vehicle_line_id', 'in', selected_vechiclemodel))
        obj_vehicle_specifications = request.env['zue.vehicle.specifications'].sudo().search(domain_vehicle_specifications)
        obj_vehicle_type = request.env['ir.model.fields.selection'].sudo().search([('field_id.model', '=', 'fleet.vehicle.model'),('field_id.name', '=', 'vehicle_type')])
        obj_stock_vehicle_type = request.env['stock.type'].sudo().search([])
        #Atributos productos
        obj_attributes_autoparts_conectores = request.env['zue.settings.autoparts'].sudo().search([('z_type','=','1')])
        obj_attributes_autoparts_protocolos = request.env['zue.settings.autoparts'].sudo().search([('z_type', '=', '2')])
        obj_attributes_autoparts_sistemaelec = request.env['zue.settings.autoparts'].sudo().search([('z_type', '=', '3')])
        obj_attributes_autoparts_voltaje = request.env['zue.settings.autoparts'].sudo().search([('z_type', '=', '4')])
        obj_attributes_autoparts_otros = request.env['zue.settings.autoparts'].sudo().search([('z_type', '=', '100')])
        obj_attributes_autoparts_otros_values = request.env['zue.attributes.product.autoparts'].sudo().search([('z_attribute_setting_id', 'in', obj_attributes_autoparts_otros.ids),('z_value','!=',False)])
        #Atributos de vehiculos
        obj_attributes_fleet = request.env['zue.settings.fleet'].sudo().search([('z_publish_ecommerce','=',True)])
        obj_attributes_fleet_aspimotor = request.env['zue.settings.fleet'].sudo().search([('z_type', '=', '1'),('z_publish_ecommerce','=',True)])
        obj_attributes_fleet_cabezamotor = request.env['zue.settings.fleet'].sudo().search([('z_type', '=', '2'),('z_publish_ecommerce','=',True)])
        obj_attributes_fleet_carroceria = request.env['zue.settings.fleet'].sudo().search([('z_type', '=', '3'),('z_publish_ecommerce','=',True)])
        obj_attributes_fleet_combustible = request.env['zue.settings.fleet'].sudo().search([('z_type', '=', '4'),('z_publish_ecommerce','=',True)])
        obj_attributes_fleet_nivelemisiones = request.env['zue.settings.fleet'].sudo().search([('z_type', '=', '7'),('z_publish_ecommerce','=',True)])
        obj_attributes_fleet_transmision = request.env['zue.settings.fleet'].sudo().search([('z_type', '=', '5'),('z_publish_ecommerce','=',True)])
        obj_attributes_fleet_traccion = request.env['zue.settings.fleet'].sudo().search([('z_type', '=', '6'),('z_publish_ecommerce','=',True)])
        obj_attributes_fleet_tipofreno = request.env['zue.settings.fleet'].sudo().search([('z_type', '=', '8'),('z_publish_ecommerce','=',True)])
        obj_attributes_fleet_tipovehiculo = request.env['zue.settings.fleet'].sudo().search([('z_type', '=', '9'),('z_publish_ecommerce','=',True)])
        obj_attributes_fleet_otros = request.env['zue.settings.fleet'].sudo().search([('z_type', '=', '100'),('z_publish_ecommerce','=',True)])
        obj_attributes_fleet_otros_values = request.env['zue.attributes.vehicle.fleet'].sudo().search([('z_attribute_setting_id', 'in', obj_attributes_fleet_otros.ids), ('z_value', '!=', False)])

        # Parametrizacion vista de filtros y ubicacion
        obj_filter_parameterization = request.env['zue.filter.parameterization'].sudo().search([('z_company_id','=',request.env.company.id)],limit=1)

        response.qcontext.update(
            obj_brands=obj_brands,
            selected_brands=selected_brands,
            obj_vehicle_type=obj_vehicle_type,
            selected_vehicletype=selected_vehicletype,
            obj_stock_vehicle_type=obj_stock_vehicle_type,
            selected_stock_vehicletype=selected_stock_vehicletype,
            selected_vechicleyear=selected_vechicleyear,
            obj_vehicle_model=obj_vehicle_model,
            selected_vechiclemodel=selected_vechiclemodel,
            obj_segments=obj_segments,
            selected_system=selected_system,
            obj_subsegments=obj_subsegments,
            selected_division=selected_division,
            obj_class=obj_class,
            selected_family=selected_family,
            obj_brands_vehicle=obj_brands_vehicle,
            selected_brandsvehicle=selected_brandsvehicle,
            obj_attributes_autoparts_conectores=obj_attributes_autoparts_conectores,
            obj_vehicle_specifications=obj_vehicle_specifications,
            selected_vehicle_specifications=selected_vehicle_specifications,
            selected_conectores=selected_conectores,
            obj_attributes_autoparts_protocolos=obj_attributes_autoparts_protocolos,
            selected_protocolos=selected_protocolos,
            obj_attributes_autoparts_sistemaelec=obj_attributes_autoparts_sistemaelec,
            selected_sistemaelec=selected_sistemaelec,
            obj_attributes_autoparts_voltaje=obj_attributes_autoparts_voltaje,
            selected_voltaje=selected_voltaje,
            obj_attributes_autoparts_otros=obj_attributes_autoparts_otros,
            selected_attributes=selected_attributes,
            obj_attributes_autoparts_otros_values=obj_attributes_autoparts_otros_values,
            selected_autoparts_otros=selected_autoparts_otros,
            obj_attributes_fleet=obj_attributes_fleet,
            obj_attributes_fleet_aspimotor=obj_attributes_fleet_aspimotor,
            selected_fleet_aspimotor=selected_fleet_aspimotor,
            obj_attributes_fleet_cabezamotor=obj_attributes_fleet_cabezamotor,
            selected_fleet_cabezamotor=selected_fleet_cabezamotor,
            obj_attributes_fleet_carroceria=obj_attributes_fleet_carroceria,
            selected_fleet_carroceria=selected_fleet_carroceria,
            obj_attributes_fleet_combustible=obj_attributes_fleet_combustible,
            selected_fleet_combustible=selected_fleet_combustible,
            obj_attributes_fleet_nivelemisiones=obj_attributes_fleet_nivelemisiones,
            selected_fleet_nivelemisiones=selected_fleet_nivelemisiones,
            obj_attributes_fleet_transmision=obj_attributes_fleet_transmision,
            selected_fleet_transmision=selected_fleet_transmision,
            obj_attributes_fleet_traccion=obj_attributes_fleet_traccion,
            selected_fleet_traccion=selected_fleet_traccion,
            obj_attributes_fleet_tipofreno=obj_attributes_fleet_tipofreno,
            selected_fleet_tipofreno=selected_fleet_tipofreno,
            obj_attributes_fleet_tipovehiculo=obj_attributes_fleet_tipovehiculo,
            selected_fleet_tipovehiculo=selected_fleet_tipovehiculo,
            obj_attributes_fleet_otros=obj_attributes_fleet_otros,
            selected_fleet_otros=selected_fleet_otros,
            selected_attributes_fleet=selected_attributes_fleet,
            obj_attributes_fleet_otros_values=obj_attributes_fleet_otros_values,
            obj_filter_parameterization=obj_filter_parameterization,
            next_year=datetime.datetime.now().year+2,
        )
        return response
