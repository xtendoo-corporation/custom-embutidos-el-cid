# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoicing_directly = fields.Boolean(string="Factura directa", default=True)
