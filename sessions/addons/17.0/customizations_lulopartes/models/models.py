# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class customizations_lulopartes(models.Model):
#     _name = 'customizations_lulopartes.customizations_lulopartes'
#     _description = 'customizations_lulopartes.customizations_lulopartes'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

