from odoo import api, models, fields, tools, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('vat', 'country_id')
    def check_vat(self):
        return

