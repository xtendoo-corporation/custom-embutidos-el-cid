# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    restrict_lot_id = fields.Many2one(
        "stock.lot",
        string="Restrict Lot",
        copy=False,
        check_company=True,
        index="btree_not_null",
    )

    def _update_reserved_quantity(
        self, need, location_id, lot_id=None, package_id=None, owner_id=None, strict=True
    ):
        self.ensure_one()
        lot = lot_id or self.restrict_lot_id
        return super()._update_reserved_quantity(
            need,
            location_id,
            lot_id=lot,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict or bool(lot),
        )

    def _set_restrict_lot_id_from_sol(self, lot):
        """This method can be extended and/or used by other modules to intercept
        the change from the sales order line.
        """
        self.restrict_lot_id = lot
        self._do_unreserve()
        self.filtered(
            lambda move: move.state in ("confirmed", "partially_available", "assigned")
        )._action_assign()
