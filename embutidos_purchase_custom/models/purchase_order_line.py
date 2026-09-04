from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    expiration_date = fields.Datetime(
        related="lot_id.expiration_date",
        string="Expiration Date",
        store=True,
        readonly=False,
        copy=False,
    )

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        vals = super()._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
        if self.lot_id:
            vals["restrict_lot_id"] = self.lot_id.id
        return vals
