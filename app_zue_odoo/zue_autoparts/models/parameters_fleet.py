from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class zue_settings_fleet(models.Model):
    _name = 'zue.settings.fleet'
    _description = 'Configuración atributos flota'

    z_type = fields.Selection([('1','Aspiración del Motor'),
                               ('2', 'Cabeza de Motor'),
                               ('3', 'Carrocería'),
                               ('4', 'Combustible'),
                               ('7', 'Nivel Emisiones'),
                               ('5', 'Transmisión '),
                               ('6', 'Tracción'),
                               ('8', 'Tipo Freno'),
                               ('9', 'Tipo de Vehículo'),
                               ('100', 'Otro')], string="Tipo", required=True)
    z_name = fields.Char(string="Nombre")
    z_publish_ecommerce = fields.Boolean(string='Publicar en E-commerce', default=True)
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
                name = record.z_name or 'Otro'
            record.display_name = name

class zue_attributes_fleet(models.Model):
    _name = 'zue.attributes.fleet'
    _description = 'Atributos de la linea del vehículo'
    _rec_name = 'z_rec_name'
    _order = 'z_sequence'

    z_sequence = fields.Integer(string='Secuencia')
    z_fleet_vehicle_id = fields.Many2one('fleet.vehicle.model', string='Linea del vehículo', required=True)
    z_type = fields.Selection([('1', 'Aspiración del Motor'),
                               ('2', 'Cabeza de Motor'),
                               ('3', 'Carrocería'),
                               ('4', 'Combustible'),
                               ('7', 'Nivel Emisiones'),
                               ('5', 'Transmisión '),
                               ('6', 'Tracción'),
                               ('8', 'Tipo Freno'),
                               ('9', 'Tipo de Vehículo'),
                               ('100', 'Otro')], string="Tipo", required=True)
    z_attribute_setting_id = fields.Many2one('zue.settings.fleet', string='Atributo OTRO', domain="[('z_type','=',z_type)]")
    z_rec_name = fields.Char('Atributo', compute='_get_z_rec_name')

    @api.depends('z_type', 'z_attribute_setting_id')
    def _get_z_rec_name(self):
        for record in self:
            if record.z_type != '100':
                name = dict(self._fields['z_type'].selection).get(record.z_type)
            else:
                name = record.z_attribute_setting_id.display_name
            record.z_rec_name = name

    @api.model
    def create(self, vals):
        res = super(zue_attributes_fleet, self).create(vals)
        for record in res:
            obj_products = self.env['zue.vehicle.specifications'].search([('z_vehicle_line_id', '=', record.z_fleet_vehicle_id.id)])
            lst_available_type = []
            lst_available_type.append((0, 0, {'z_sequence': record.z_sequence,
                                              'z_type': record.z_type,
                                              'z_attribute_setting_id': record.z_attribute_setting_id.id if record.z_attribute_setting_id else False}))
            if len(lst_available_type) > 0:
                for product in obj_products:
                    product.z_attributes_vehicle_ids = lst_available_type
        return res

    def unlink(self):
        for record in self:
            obj_products = self.env['zue.vehicle.specifications'].search([('z_vehicle_line_id', '=', record.z_fleet_vehicle_id.id)])
            for product in obj_products:
                for attributes in product.z_attributes_vehicle_ids:
                    if (attributes.z_type == record.z_type and record.z_type != '100') or (record.z_type == '100' and attributes.z_attribute_setting_id.id == record.z_attribute_setting_id.id):
                        attributes.unlink()
        return super(zue_attributes_fleet, self).unlink()
    def write(self, vals):
        res = super(zue_attributes_fleet, self).write(vals)
        for record in self:
            obj_products = self.env['zue.vehicle.specifications'].search([('z_vehicle_line_id', '=', record.z_fleet_vehicle_id.id)])
            for product in obj_products:
                for attributes in product.z_attributes_vehicle_ids:
                    if (attributes.z_type == record.z_type and record.z_type != '100') or (
                            record.z_type == '100' and attributes.z_attribute_setting_id.id == record.z_attribute_setting_id.id):
                        attributes.write({'z_sequence': record.z_sequence})
        return res

class fleet_vehicle_model(models.Model):
    _inherit = 'fleet.vehicle.model'

    vehicle_type = fields.Selection(selection_add=[('bus', 'Bus'),
                                                   ('shuttle', 'Buseta'),
                                                   ('truck', 'Camion'),
                                                   ('van', 'Camioneta'),
                                                   ('camper', 'Campero'),
                                                   ('moped', 'Ciclomotor'),
                                                   ('quadricycle', 'Cuadriciclo'),
                                                   ('ATV', 'Cuatrimoto'),
                                                   ('agricultural_machinery', 'Maquinaria agricola'),
                                                   ('construction_machinery', 'Maquinaria construcción'),
                                                   ('microbus', 'Microbus'),
                                                   ('motorcycle', 'Moto'),
                                                   ('motocart', 'Motocarro'),
                                                   ('motobike', 'Motocicleta'),
                                                   ('motor_tricycle', 'Mototriciclo'),
                                                   ('trailer_emi_trailer', 'Remolque y semirremolque'),
                                                   ('tractor_trailer', 'Tractocamion'),
                                                  ('dump_truck', 'Volqueta'),
                                                 ('suv', 'SUV')],
                                   ondelete={"bus": "set default", "shuttle": "set default",
                                              "truck": "set default","van": "set default","camper": "set default","moped": "set default","quadricycle": "set default","ATV": "set default",
                                             "agricultural_machinery": "set default","construction_machinery": "set default","microbus": "set default","motorcycle": "set default",
                                             "motocart": "set default","motobike": "set default","motor_tricycle": "set default","trailer_emi_trailer": "set default",
                                             "tractor_trailer": "set default","dump_truck": "set default","suv": "set default",}, string='Vehicle Type')

    z_final_model_year = fields.Integer(string="Año del modelo - Hasta")
    z_attributes_ids = fields.One2many('zue.attributes.fleet', 'z_fleet_vehicle_id', string="Atributos")
    z_origin_country = fields.Many2one('res.country', string="País de procedencia")

class zue_attributes_vehicle_fleet(models.Model):
    _name = 'zue.attributes.vehicle.fleet'
    _description = 'Atributos de vehículo'
    _rec_name = 'z_rec_name'
    _order = 'z_sequence'

    z_vehicle_id = fields.Many2one('zue.vehicle.specifications', string='Vehículo', required=True)
    z_sequence = fields.Integer(string='Secuencia', readonly=True)
    z_type = fields.Selection([('1', 'Aspiración del Motor'),
                               ('2', 'Cabeza de Motor'),
                               ('3', 'Carrocería'),
                               ('4', 'Combustible'),
                               ('7', 'Nivel Emisiones'),
                               ('5', 'Transmisión '),
                               ('6', 'Tracción'),
                               ('8', 'Tipo Freno'),
                               ('9', 'Tipo de Vehículo'),
                               ('100', 'Otro')], string="Tipo", required=True)
    z_attribute_setting_id = fields.Many2one('zue.settings.fleet', string='Atributo', domain="[('z_type','=',z_type),('z_type','!=','100')]")
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

class fleet_vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    z_specifications = fields.Many2one('zue.vehicle.specifications', string='Especificaciones')

class zue_vehicle_specifications(models.Model):
    _name = 'zue.vehicle.specifications'
    _description = 'Especificaciones del vehículo'

    z_name = fields.Char(string='Nombre')
    z_vehicle_line_id = fields.Many2one('fleet.vehicle.model', string='Línea del vehículo')
    z_attributes_vehicle_ids = fields.One2many('zue.attributes.vehicle.fleet', 'z_vehicle_id', string="Atributos")

    @api.depends('z_name','z_vehicle_line_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = "{} | Linea del vehículo: {}".format(record.z_name, record.z_vehicle_line_id.name)

    @api.onchange('z_vehicle_line_id')
    def _compute_available_attributes_ids(self):
        for record in self:
            record.z_attributes_vehicle_ids = [(5, 0, 0)]
            if record.z_vehicle_line_id:
                lst_available_type = []
                obj_available_attributes = self.env['zue.attributes.fleet'].search(
                    [('id', 'in', record.z_vehicle_line_id.z_attributes_ids.ids)])
                for aa in obj_available_attributes:
                    lst_available_type.append((0, 0, {'z_sequence': aa.z_sequence,
                                                      'z_type': aa.z_type,
                                                      'z_attribute_setting_id': aa.z_attribute_setting_id.id if aa.z_attribute_setting_id else False}))
                if len(lst_available_type) > 0:
                    record.z_attributes_vehicle_ids = lst_available_type

class FleetVehicleModelBrand(models.Model):
    _inherit = 'fleet.vehicle.model.brand'

    z_check_visible = fields.Boolean(string='Ocultar en autopartes')

