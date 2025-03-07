from odoo import _, tools, http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.exceptions import ValidationError

class WebsiteSaleLuloPartes(WebsiteSale):

    def _get_country_related_render_values(self, kw, render_values):
        values = render_values['checkout']
        res = super()._get_country_related_render_values(kw, render_values)
        res['document_type'] = 'l10n_latam_identification_type_id' in values and values['l10n_latam_identification_type_id'] != '' and request.env['l10n_latam.identification.type'].browse(int(values['l10n_latam_identification_type_id']))
        res['document_types'] = request.env['l10n_latam.identification.type'].search([('active', '=', True)])
        return res

    def _get_vat_validation_fields(self, data):
        res = super()._get_vat_validation_fields(data)
        res['l10n_latam_identification_type_id'] = int(data['l10n_latam_identification_type_id']) if data.get('l10n_latam_identification_type_id') else False
        return res

