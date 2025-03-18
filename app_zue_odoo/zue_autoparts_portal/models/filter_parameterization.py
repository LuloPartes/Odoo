from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class zue_filter_parameterization(models.Model):
    _name = 'zue.filter.parameterization'
    _description = 'Parametrización de Fitros E-commerce'
    _rec_name = 'z_company_id'

    z_company_id = fields.Many2one('res.company', 'Compañia')
    z_sequence = fields.Integer('Secuencia')
    z_make_autoparts = fields.Boolean('Marca', default=True)
    z_system_autoparts = fields.Boolean('Sistema', default=True)
    z_division_autoparts = fields.Boolean('División', default=True)
    z_family_autoparts = fields.Boolean('Familia', default=True)
    z_features_autopars = fields.Boolean('Características', default=True)
    z_vehicle_specifications = fields.Boolean('Especificaciones del vehículo (Marca y Línea)', default=True)
    z_stock_vehicle_type = fields.Boolean('Tipos de vehículos parametrizables', default=False)
    z_static_vehicle_type = fields.Boolean('Tipos de vehículos estáticos', default=False)
    z_vehicle_specifications_view = fields.Selection([('aside', 'Columna Lateral'),
                                                      ('top', 'Bloque superior'),
                                                      ('both', 'Ambos')],
                                                     'Formato vista - Especificaciones del vehículo', default='both')
    z_features_vehicle = fields.Boolean('Características Vehículo', default=True)
    z_initial_year = fields.Integer('Año inicial', default=1955)

