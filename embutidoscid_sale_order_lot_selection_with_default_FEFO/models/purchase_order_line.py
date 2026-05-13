from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_tracking = fields.Selection(
        related="product_id.tracking",
        string="Product Tracking",
        readonly=True,
    )
    lot_id = fields.Many2one(
        "stock.lot",
        string="Lot",
        domain="[('product_id', '=', product_id), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        copy=False,
        store=True,
        readonly=False,
    )
    expiration_date = fields.Datetime(
        related="lot_id.expiration_date",
        string="Expiration Date",
        store=True,
        readonly=True,
        copy=False,
    )

    @api.onchange("product_id")
    def _onchange_product_id_clear_lot_id(self):
        for line in self:
            if line.lot_id and line.lot_id.product_id != line.product_id:
                line.lot_id = False

    @api.constrains("product_id", "lot_id")
    def _check_lot_id_product(self):
        for line in self:
            if line.lot_id and line.lot_id.product_id != line.product_id:
                raise ValidationError(
                    self.env._("The selected Lot/Serial number does not belong to the product.")
                )

