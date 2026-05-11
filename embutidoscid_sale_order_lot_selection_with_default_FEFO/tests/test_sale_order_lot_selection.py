# © 2015 Agile Business Group
# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderLotSelection(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Tracked product",
                "tracking": "lot",
                "is_storable": True,
                "use_expiration_date": True,
                "expiration_time": 30,
            }
        )

    @classmethod
    def _create_lot(cls, name):
        return cls.env["stock.lot"].create(
            {
                "name": name,
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
            }
        )

    def _update_stock_quantity(self, lot, qty, in_date=None):
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_location, qty, lot_id=lot, in_date=in_date
        )

    def _set_lot_expiration(self, lot, expiration_date):
        values = {
            "expiration_date": expiration_date,
            "use_date": expiration_date and expiration_date - timedelta(days=2),
            "removal_date": expiration_date and expiration_date - timedelta(days=1),
            "alert_date": expiration_date and expiration_date - timedelta(days=3),
        }
        lot.write(values)

    def _new_sale_line_with_onchange(self, qty=1.0, product=None):
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
        line = self.env["sale.order.line"].new(
            {
                "order_id": order.id,
                "product_id": (product or self.product).id,
                "product_uom_qty": qty,
            }
        )
        line._onchange_product_id_clear_lot_id()
        return line

    def _get_available_qty(self, lot):
        return self.env["stock.quant"]._get_available_quantity(
            self.product, self.stock_location, lot_id=lot, strict=True
        )

    def _create_sale(self, lot):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "lot_id": lot.id,
                        }
                    )
                ],
            }
        )
        return order, order.order_line

    def _get_move(self, line):
        self.assertEqual(len(line.move_ids), 1)
        return line.move_ids

    def _validate_picking(self, picking):
        picking.move_ids.quantity = picking.move_ids.product_uom_qty
        picking.move_ids.picked = True
        picking.button_validate()

    def test_01_do_not_reserve_another_lot(self):
        requested_lot = self._create_lot("LOT-REQ")
        other_lot = self._create_lot("LOT-OTHER")
        self._update_stock_quantity(other_lot, 1.0)

        order, line = self._create_sale(requested_lot)
        order.action_confirm()
        move = self._get_move(line)

        self.assertEqual(move.restrict_lot_id, requested_lot)
        self.assertEqual(move.state, "confirmed")
        self.assertFalse(move.move_line_ids)
        self.assertEqual(self._get_available_qty(other_lot), 1.0)

    def test_02_reserve_selected_lot(self):
        lot_1 = self._create_lot("LOT-1")
        lot_2 = self._create_lot("LOT-2")
        self._update_stock_quantity(lot_1, 1.0)
        self._update_stock_quantity(lot_2, 1.0)

        order, line = self._create_sale(lot_1)
        order.action_confirm()
        move = self._get_move(line)

        self.assertEqual(move.state, "assigned")
        self.assertEqual(move.restrict_lot_id, lot_1)
        self.assertEqual(move.move_line_ids.lot_id, lot_1)
        self.assertEqual(self._get_available_qty(lot_1), 0.0)
        self.assertEqual(self._get_available_qty(lot_2), 1.0)

    def test_03_change_lot_before_done_reassigns_reservation(self):
        lot_1 = self._create_lot("LOT-BEFORE-1")
        lot_2 = self._create_lot("LOT-BEFORE-2")
        self._update_stock_quantity(lot_1, 1.0)
        self._update_stock_quantity(lot_2, 1.0)

        order, line = self._create_sale(lot_1)
        order.action_confirm()
        move = self._get_move(line)
        self.assertEqual(move.move_line_ids.lot_id, lot_1)

        line.lot_id = lot_2

        self.assertEqual(move.restrict_lot_id, lot_2)
        self.assertEqual(move.state, "assigned")
        self.assertEqual(move.move_line_ids.lot_id, lot_2)
        self.assertEqual(self._get_available_qty(lot_1), 1.0)
        self.assertEqual(self._get_available_qty(lot_2), 0.0)

    def test_04_cannot_change_lot_after_done(self):
        lot_1 = self._create_lot("LOT-DONE-1")
        lot_2 = self._create_lot("LOT-DONE-2")
        self._update_stock_quantity(lot_1, 1.0)
        self._update_stock_quantity(lot_2, 1.0)

        order, line = self._create_sale(lot_1)
        order.action_confirm()
        self._validate_picking(order.picking_ids)

        msg = (
            "You can't modify the Lot/Serial number "
            "because some stock move has already been done."
        )
        with self.assertRaisesRegex(ValidationError, msg):
            line.lot_id = lot_2

    def test_05_onchange_product_sets_fefo_lot(self):
        earlier_expiry_lot = self._create_lot("LOT-FEFO-EARLY")
        later_expiry_lot = self._create_lot("LOT-FEFO-LATE")
        now = fields.Datetime.now()
        self._set_lot_expiration(earlier_expiry_lot, now + timedelta(days=5))
        self._set_lot_expiration(later_expiry_lot, now + timedelta(days=10))
        self._update_stock_quantity(earlier_expiry_lot, 1.0, in_date=now - timedelta(days=1))
        self._update_stock_quantity(later_expiry_lot, 1.0, in_date=now - timedelta(days=5))

        line = self._new_sale_line_with_onchange()

        self.assertEqual(line.lot_id, earlier_expiry_lot)

    def test_06_onchange_product_skips_fefo_lot_without_enough_qty(self):
        earlier_expiry_lot = self._create_lot("LOT-FEFO-SHORT")
        later_expiry_lot = self._create_lot("LOT-FEFO-ENOUGH")
        now = fields.Datetime.now()
        self._set_lot_expiration(earlier_expiry_lot, now + timedelta(days=5))
        self._set_lot_expiration(later_expiry_lot, now + timedelta(days=10))
        self._update_stock_quantity(earlier_expiry_lot, 1.0, in_date=now - timedelta(days=2))
        self._update_stock_quantity(later_expiry_lot, 2.0, in_date=now - timedelta(days=1))

        line = self._new_sale_line_with_onchange(qty=2.0)

        self.assertEqual(line.lot_id, later_expiry_lot)

    def test_07_onchange_product_places_lot_without_expiration_at_end(self):
        dated_lot = self._create_lot("LOT-FEFO-DATED")
        lot_without_date = self._create_lot("LOT-FEFO-NO-DATE")
        now = fields.Datetime.now()
        self._set_lot_expiration(dated_lot, now + timedelta(days=5))
        self._set_lot_expiration(lot_without_date, False)
        self._update_stock_quantity(dated_lot, 1.0, in_date=now - timedelta(days=1))
        self._update_stock_quantity(lot_without_date, 1.0, in_date=now - timedelta(days=3))

        line = self._new_sale_line_with_onchange()

        self.assertEqual(line.lot_id, dated_lot)

    def test_08_onchange_product_uses_lot_without_expiration_as_fallback(self):
        lot_without_date = self._create_lot("LOT-FEFO-FALLBACK")
        self._set_lot_expiration(lot_without_date, False)
        self._update_stock_quantity(lot_without_date, 1.0)

        line = self._new_sale_line_with_onchange()

        self.assertEqual(line.lot_id, lot_without_date)

    def test_09_onchange_product_without_available_lot_keeps_empty(self):
        self._create_lot("LOT-NO-STOCK")

        line = self._new_sale_line_with_onchange()

        self.assertFalse(line.lot_id)

    def test_10_line_expiration_date_follows_selected_lot(self):
        lot_1 = self._create_lot("LOT-EXP-1")
        lot_2 = self._create_lot("LOT-EXP-2")
        now = fields.Datetime.now()
        expiration_1 = now + timedelta(days=5)
        expiration_2 = now + timedelta(days=10)
        self._set_lot_expiration(lot_1, expiration_1)
        self._set_lot_expiration(lot_2, expiration_2)
        self._update_stock_quantity(lot_1, 1.0)
        self._update_stock_quantity(lot_2, 1.0)

        order, line = self._create_sale(lot_1)

        self.assertEqual(line.expiration_date, lot_1.expiration_date)

        line.lot_id = lot_2

        self.assertEqual(order.order_line.expiration_date, lot_2.expiration_date)

