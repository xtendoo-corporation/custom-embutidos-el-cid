from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    repartidor_empleado_id = fields.Many2one(
        "hr.employee",
        string="Repartidor",
    )
    show_sale_buttons = fields.Boolean(
        related="partner_id.show_sale_buttons",
        string="Mostrar botones de venta",
    )
