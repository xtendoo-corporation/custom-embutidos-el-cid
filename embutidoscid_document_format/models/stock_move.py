from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    sale_price_unit = fields.Float(
        string="Precio unitario",
        compute="_compute_sale_prices",
        digits="Product Price",
    )
    sale_discount = fields.Float(
        string="Descuento (%)",
        compute="_compute_sale_prices",
    )
    sale_price_subtotal = fields.Monetary(
        string="Subtotal",
        compute="_compute_sale_prices",
        currency_field="sale_currency_id",
    )
    sale_price_total = fields.Monetary(
        string="Total",
        compute="_compute_sale_prices",
        currency_field="sale_currency_id",
    )
    sale_currency_id = fields.Many2one(
        "res.currency",
        compute="_compute_sale_prices",
        string="Moneda",
    )

    @api.depends("sale_line_id", "sale_line_id.price_unit", "sale_line_id.discount",
                 "sale_line_id.price_subtotal", "sale_line_id.price_total",
                 "sale_line_id.currency_id", "quantity")
    def _compute_sale_prices(self):
        for move in self:
            if move.sale_line_id:
                sale_line = move.sale_line_id
                # Calcula proporción si la cantidad del move es diferente a la de la línea
                qty_ratio = 1.0
                if sale_line.product_uom_qty:
                    qty_ratio = move.quantity / sale_line.product_uom_qty

                move.sale_price_unit = sale_line.price_unit
                move.sale_discount = sale_line.discount
                move.sale_price_subtotal = sale_line.price_subtotal * qty_ratio
                move.sale_price_total = sale_line.price_total * qty_ratio
                move.sale_currency_id = sale_line.currency_id
            else:
                move.sale_price_unit = 0.0
                move.sale_discount = 0.0
                move.sale_price_subtotal = 0.0
                move.sale_price_total = 0.0
                move.sale_currency_id = False

