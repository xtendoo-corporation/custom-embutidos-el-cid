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
    sale_price_tax_iva = fields.Monetary(
        string="IVA",
        compute="_compute_sale_prices",
        currency_field="sale_currency_id",
    )
    sale_price_tax_re = fields.Monetary(
        string="Recargo",
        compute="_compute_sale_prices",
        currency_field="sale_currency_id",
    )
    sale_currency_id = fields.Many2one(
        "res.currency",
        compute="_compute_sale_prices",
        string="Moneda",
    )
    sale_tax_id = fields.Many2many(
        "account.tax",
        compute="_compute_sale_prices",
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
                move.sale_tax_id = sale_line.tax_ids

                # Desglose de impuestos (IVA y Recargo)
                iva_amount = 0.0
                re_amount = 0.0
                taxes_res = sale_line.tax_ids.compute_all(
                    sale_line.price_unit * (1 - (sale_line.discount or 0.0) / 100.0),
                    quantity=move.quantity,
                    product=move.product_id,
                    partner=sale_line.order_id.partner_id
                )
                for tax_val in taxes_res['taxes']:
                    tax = self.env['account.tax'].browse(tax_val['id'])
                    if tax.tax_group_id and 'recargo' in tax.tax_group_id.name.lower():
                        re_amount += tax_val['amount']
                    else:
                        iva_amount += tax_val['amount']

                move.sale_price_tax_iva = iva_amount
                move.sale_price_tax_re = re_amount
            else:
                move.sale_price_unit = 0.0
                move.sale_discount = 0.0
                move.sale_price_subtotal = 0.0
                move.sale_price_total = 0.0
                move.sale_price_tax_iva = 0.0
                move.sale_price_tax_re = 0.0
                move.sale_currency_id = False
                move.sale_tax_id = False
