from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _selection_product_tracking(self):
        return self.env["product.product"].fields_get(
            allfields=["tracking"],
        )["tracking"]["selection"]

    product_tracking = fields.Selection(
        selection=_selection_product_tracking,
        compute="_compute_product_tracking",
    )
    domain_lot_id = fields.Binary(compute="_compute_domain_lot_id")
    lot_id = fields.Many2one(
        "stock.lot",
        "Lot",
        domain="domain_lot_id",
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

    def _prepare_procurement_values(self):
        vals = super()._prepare_procurement_values()
        if self.lot_id:
            vals["restrict_lot_id"] = self.lot_id.id
        return vals

    def _get_available_lot_quants(self):
        self.ensure_one()
        quants = self.env["stock.quant"]
        if (
            not self.product_id
            or self.product_tracking == "none"
            or not self.warehouse_id
        ):
            return quants
        qty = self.product_uom_qty or 1.0
        rounding = self.product_uom_id.rounding or self.product_id.uom_id.rounding
        quants = quants.search(
            [
                ("product_id", "=", self.product_id.id),
                ("lot_id", "!=", False),
                ("location_id.usage", "=", "internal"),
                ("location_id.warehouse_id", "=", self.warehouse_id.id),
            ]
        )
        return quants.filtered(
            lambda quant, precision_rounding=rounding: float_compare(
                quant.available_quantity,
                0.0,
                precision_rounding=precision_rounding,
            )
            > 0
        )

    def _get_available_lot_data(self):
        self.ensure_one()
        rounding = self.product_uom_id.rounding or self.product_id.uom_id.rounding
        lot_data = {}
        for quant in self._get_available_lot_quants():
            lot = quant.lot_id
            data = lot_data.setdefault(
                lot.id,
                {
                    "lot": lot,
                    "available_qty": 0.0,
                    "expiration_date": lot.expiration_date,
                    "in_date": quant.in_date,
                },
            )
            data["available_qty"] += quant.available_quantity
            quant_in_date = quant.in_date
            if quant_in_date and (not data["in_date"] or quant_in_date < data["in_date"]):
                data["in_date"] = quant_in_date
        qty = self.product_uom_qty or 1.0
        return [
            data
            for data in lot_data.values()
            if float_compare(
                data["available_qty"],
                qty,
                precision_rounding=rounding,
            )
            >= 0
        ]

    def _get_fefo_lot_id(self):
        self.ensure_one()
        available_lots = sorted(
            self._get_available_lot_data(),
            key=lambda data: (
                data["expiration_date"] is False,
                fields.Datetime.to_datetime(data["expiration_date"]) or datetime.max,
                fields.Datetime.to_datetime(data["in_date"]) or datetime.max,
                data["lot"].id,
            ),
        )
        return available_lots[0]["lot"] if available_lots else self.env["stock.lot"]

    @api.depends("product_id")
    def _compute_product_tracking(self):
        for sol in self:
            sol.product_tracking = sol.product_id.tracking or sol.product_tracking

    @api.depends("product_id", "product_uom_qty", "warehouse_id")
    def _compute_domain_lot_id(self):
        for sol in self:
            domain = []
            if sol.product_id and sol.product_tracking != "none":
                domain = [
                    ("id", "in", [data["lot"].id for data in sol._get_available_lot_data()])
                ]
            sol.domain_lot_id = domain

    @api.onchange("product_id")
    def _onchange_product_id_clear_lot_id(self):
        for sol in self:
            if sol.lot_id and sol.product_id != sol.lot_id.product_id:
                sol.lot_id = False
            if not sol.lot_id:
                sol.lot_id = sol._get_fefo_lot_id()

    @api.constrains("product_id", "lot_id")
    def _check_lot_id_product(self):
        for sol in self:
            if sol.lot_id and sol.lot_id.product_id != sol.product_id:
                raise ValidationError(
                    self.env._("The selected Lot/Serial number does not belong to the product.")
                )

    def write(self, vals):
        lot_written = "lot_id" in vals
        res = super().write(vals)
        if lot_written:
            self._sync_moves_restrict_lot_id()
        return res

    def _sync_moves_restrict_lot_id(self):
        for item in self.filtered(
            lambda x: x.product_id and x.product_tracking != "none" and x.move_ids
        ):
            moves = item.move_ids.filtered(lambda x: x.state != "cancel")
            if any(move.state == "done" for move in moves):
                raise ValidationError(
                    self.env._(
                        "You can't modify the Lot/Serial number "
                        "because some stock move has already been done."
                    )
                )
            pending_moves = moves.filtered(lambda x: x.state != "cancel")
            if pending_moves:
                pending_moves._set_restrict_lot_id_from_sol(item.lot_id)
