# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    show_sale_buttons = fields.Boolean(
        string="Confirma, entregar y facturar activado",
        default=True,
        help="Si está marcado, se mostrarán los botones de confirmar, entregar y facturar en las órdenes de venta de este cliente.",
    )
