from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class zue_special_locations(models.Model):
    _name = 'zue.special.locations'
    _description = 'Ubicaciones especiales'
    _rec_name = 'z_code'

    z_code = fields.Char(string='Código',required=True)

    _sql_constraints = [('zue_special_locations_uniq', 'unique(z_code)',
                         'Este código ya existe, por favor verificar.')]