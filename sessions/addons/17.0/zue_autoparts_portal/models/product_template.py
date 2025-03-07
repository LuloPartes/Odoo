from odoo import api, fields, models, Command
from odoo.addons.website.models import ir_http


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    z_available_websites_ids = fields.Many2many('website', string='Sitios webs disponibles')

    @api.model
    def _search_get_detail(self, website, order, options):
        res = super()._search_get_detail(website, order, options)
        res['base_domain'].append([('z_available_websites_ids', '=', website.id)])
        if options.get('zue_shop_args'):
            args = options.get('zue_shop_args')
            selected_brands = [int(x) for x in args.getlist('brand') if int(x) != 0]
            selected_vehicletype = [int(x) for x in args.getlist('vehicletype') if int(x) != 0]
            selected_stock_vehicletype = [int(x) for x in args.getlist('stock_vehicletype') if int(x) != 0]
            selected_vechicleyear = [int(x) for x in args.getlist('vehicleyear') if int(x) != 0]
            selected_vechiclemodel = [int(x) for x in args.getlist('vechiclemodel') if int(x) != 0]
            selected_vehicle_specifications = [int(x) for x in args.getlist('vehiclespecifications') if int(x) != 0]
            selected_system = [int(x) for x in args.getlist('system') if int(x) != 0]
            selected_division = [int(x) for x in args.getlist('division') if int(x) != 0]
            selected_family = [int(x) for x in args.getlist('family') if int(x) != 0]
            selected_brandsvehicle = [int(x) for x in args.getlist('brandvehicle') if int(x) != 0]
            selected_conectores = [int(x) for x in args.getlist('conectores') if int(x) != 0]
            selected_protocolos = [int(x) for x in args.getlist('protocolos') if int(x) != 0]
            selected_sistemaelec = [int(x) for x in args.getlist('sistemaelec') if int(x) != 0]
            selected_voltaje = [int(x) for x in args.getlist('voltaje') if int(x) != 0]
            selected_autoparts_otros = [x for x in args.getlist('autoparts_otros') if int(x) != 0]
            selected_attributes = selected_conectores + selected_protocolos + selected_sistemaelec + selected_voltaje + selected_autoparts_otros
            selected_fleet_aspimotor = [int(x) for x in args.getlist('fleet_aspimotor') if int(x) != 0]
            selected_fleet_cabezamotor = [int(x) for x in args.getlist('fleet_cabezamotor') if int(x) != 0]
            selected_fleet_carroceria = [int(x) for x in args.getlist('fleet_carroceria') if int(x) != 0]
            selected_fleet_combustible = [int(x) for x in args.getlist('fleet_combustible') if int(x) != 0]
            selected_fleet_nivelemisiones = [int(x) for x in args.getlist('fleet_nivelemisiones') if int(x) != 0]
            selected_fleet_transmision = [int(x) for x in args.getlist('fleet_transmision') if int(x) != 0]
            selected_fleet_traccion = [int(x) for x in args.getlist('fleet_traccion') if int(x) != 0]
            selected_fleet_tipofreno = [int(x) for x in args.getlist('fleet_tipofreno') if int(x) != 0]
            selected_fleet_tipovehiculo = [int(x) for x in args.getlist('fleet_tipovehiculo') if int(x) != 0]
            selected_fleet_otros = [x for x in args.getlist('fleet_otros') if int(x) != 0]
            selected_attributes_fleet = selected_fleet_aspimotor + selected_fleet_cabezamotor + selected_fleet_carroceria + selected_fleet_combustible + selected_fleet_nivelemisiones + selected_fleet_transmision + selected_fleet_traccion + selected_fleet_tipofreno + selected_fleet_tipovehiculo + selected_fleet_otros

            # Aplicar filtros productos
            if len(selected_brands) > 0:
                res['base_domain'].append([('brands_id', 'in', selected_brands)])
            if len(selected_system) > 0:
                res['base_domain'].append([('segments_id', 'in', selected_system)])
            if len(selected_division) > 0:
                res['base_domain'].append([('subsegments_id', 'in', selected_division)])
            if len(selected_family) > 0:
                res['base_domain'].append([('class_id', 'in', selected_family)])
            if len(selected_conectores) > 0:
                res['base_domain'].append([('z_attributes_product_ids.z_attribute_setting_id.id', 'in', selected_conectores)])
            if len(selected_protocolos) > 0:
                res['base_domain'].append([('z_attributes_product_ids.z_attribute_setting_id.id', 'in', selected_protocolos)])
            if len(selected_sistemaelec) > 0:
                res['base_domain'].append([('z_attributes_product_ids.z_attribute_setting_id.id', 'in', selected_sistemaelec)])
            if len(selected_voltaje) > 0:
                res['base_domain'].append([('z_attributes_product_ids.z_attribute_setting_id.id', 'in', selected_voltaje)])
            if len(selected_autoparts_otros) > 0:
                for filter in selected_autoparts_otros:
                    selected = str(filter).split('|')
                    if len(selected) == 2:
                        obj_attributes_other_filter = self.env['zue.attributes.product.autoparts'].search([('z_attribute_setting_id', '=', selected[0]),('z_value','=',selected[1])])
                        res['base_domain'].append([('z_attributes_product_ids', 'in', obj_attributes_other_filter.ids)])
            #Aplicar filtros vehiculos
            if len(selected_vehicletype) > 0:
                obj_vehicle_type = self.env['ir.model.fields.selection'].sudo().search([('field_id.model', '=', 'fleet.vehicle.model'), ('field_id.name', '=', 'vehicle_type'),('id','in',selected_vehicletype)])
                lst_vehicle_type = []
                for vehicle_type in obj_vehicle_type:
                    lst_vehicle_type.append(vehicle_type.value)
                res['base_domain'].append([('vehicle_destination_ids.vehicle_type', 'in', lst_vehicle_type)])
            if len(selected_stock_vehicletype) > 0:
                res['base_domain'].append([('type_id', 'in', selected_stock_vehicletype)])
            if len(selected_vechicleyear) > 0:
                obj_vehicle_destination_year = self.env['vehicle.destination'].sudo().search([('initial_year', '<=', selected_vechicleyear[0]),('final_year', '>=', selected_vechicleyear[0])])
                res['base_domain'].append([('vehicle_destination_ids.id', 'in', obj_vehicle_destination_year.ids)])
            if len(selected_brandsvehicle) > 0:
                res['base_domain'].append([('vehicle_destination_ids.vehicle_brand_id.id', 'in', selected_brandsvehicle)])
            if len(selected_vechiclemodel) > 0:
                res['base_domain'].append([('vehicle_destination_ids.vehicle_line_id.id', 'in', selected_vechiclemodel)])
            if len(selected_vehicle_specifications) > 0:
                res['base_domain'].append([('vehicle_destination_ids.z_vehicle_specifications_id.id', 'in', selected_vehicle_specifications)])
            if len(selected_attributes_fleet) > 0:
                domain_vehicle_specifications = []
                if len(selected_fleet_aspimotor) > 0:
                    domain_vehicle_specifications.append(('z_attributes_vehicle_ids.z_attribute_setting_id.id','in',selected_fleet_aspimotor))
                if len(selected_fleet_cabezamotor) > 0:
                    domain_vehicle_specifications.append(('z_attributes_vehicle_ids.z_attribute_setting_id.id','in',selected_fleet_cabezamotor))
                if len(selected_fleet_carroceria) > 0:
                    domain_vehicle_specifications.append(('z_attributes_vehicle_ids.z_attribute_setting_id.id','in',selected_fleet_carroceria))
                if len(selected_fleet_combustible) > 0:
                    domain_vehicle_specifications.append(('z_attributes_vehicle_ids.z_attribute_setting_id.id','in',selected_fleet_combustible))
                if len(selected_fleet_nivelemisiones) > 0:
                    domain_vehicle_specifications.append(('z_attributes_vehicle_ids.z_attribute_setting_id.id','in',selected_fleet_nivelemisiones))
                if len(selected_fleet_transmision) > 0:
                    domain_vehicle_specifications.append(('z_attributes_vehicle_ids.z_attribute_setting_id.id','in',selected_fleet_transmision))
                if len(selected_fleet_traccion) > 0:
                    domain_vehicle_specifications.append(('z_attributes_vehicle_ids.z_attribute_setting_id.id','in',selected_fleet_traccion))
                if len(selected_fleet_tipofreno) > 0:
                    domain_vehicle_specifications.append(('z_attributes_vehicle_ids.z_attribute_setting_id.id','in',selected_fleet_tipofreno))
                if len(selected_fleet_tipovehiculo) > 0:
                    domain_vehicle_specifications.append(('z_attributes_vehicle_ids.z_attribute_setting_id.id','in',selected_fleet_tipovehiculo))
                if len(selected_fleet_otros) > 0:
                    for filter in selected_fleet_otros:
                        selected = str(filter).split('|')
                        if len(selected) == 2:
                            obj_attributes_other_filter = self.env['zue.attributes.vehicle.fleet'].search(
                                [('z_attribute_setting_id', '=', selected[0]), ('z_value', '=', selected[1])])
                            domain_vehicle_specifications.append(('z_attributes_vehicle_ids','in', obj_attributes_other_filter.ids))
                obj_vehicle_specifications = self.env['zue.vehicle.specifications'].search(domain_vehicle_specifications)
                res['base_domain'].append([('vehicle_destination_ids.z_vehicle_specifications_id.id', 'in', obj_vehicle_specifications.ids)])
        return res

class ProductProduct(models.Model):
    _inherit = 'product.product'

    z_available_websites_ids = fields.Many2many(related='product_tmpl_id.z_available_websites_ids', string='Sitios webs disponibles', readonly=False)
