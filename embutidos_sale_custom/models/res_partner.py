from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    show_sale_buttons = fields.Boolean(
        string="Mostrar botones de venta",
        default=True,
        help="Si está marcado, se mostrarán los botones de confirmar, entregar y facturar en las órdenes de venta de este cliente."
    )

