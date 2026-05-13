from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseOrderLotSelection(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.partner
        cls.product = cls.env["product.product"].create(
            {
                "name": "Tracked purchase product",
                "tracking": "lot",
                "is_storable": True,
                "purchase_ok": True,
                "use_expiration_date": True,
                "expiration_time": 30,
            }
        )
        cls.other_product = cls.env["product.product"].create(
            {
                "name": "Other tracked purchase product",
                "tracking": "lot",
                "is_storable": True,
                "purchase_ok": True,
                "use_expiration_date": True,
                "expiration_time": 30,
            }
        )

    @classmethod
    def _create_lot(cls, name, product=None):
        return cls.env["stock.lot"].create(
            {
                "name": name,
                "product_id": (product or cls.product).id,
                "company_id": cls.env.company.id,
            }
        )

    def _set_lot_expiration(self, lot, expiration_date):
        values = {
            "expiration_date": expiration_date,
            "use_date": expiration_date and expiration_date - timedelta(days=2),
            "removal_date": expiration_date and expiration_date - timedelta(days=1),
            "alert_date": expiration_date and expiration_date - timedelta(days=3),
        }
        lot.write(values)

    def _create_purchase(self, lot=False, product=None):
        product = product or self.product
        line_vals = {
            "name": product.display_name,
            "product_id": product.id,
            "product_qty": 1.0,
            "product_uom_id": product.uom_id.id,
            "price_unit": 10.0,
            "date_planned": fields.Datetime.now(),
        }
        if lot:
            line_vals["lot_id"] = lot.id
        return self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [Command.create(line_vals)],
            }
        )

    def test_01_purchase_line_expiration_date_follows_selected_lot(self):
        lot = self._create_lot("PO-LOT-1")
        expiration = fields.Datetime.now() + timedelta(days=5)
        self._set_lot_expiration(lot, expiration)

        purchase = self._create_purchase(lot=lot)

        self.assertEqual(purchase.order_line.lot_id, lot)
        self.assertEqual(purchase.order_line.expiration_date, lot.expiration_date)

    def test_02_purchase_line_rejects_lot_from_other_product(self):
        wrong_lot = self._create_lot("PO-WRONG-LOT", product=self.other_product)
        msg = "The selected Lot/Serial number does not belong to the product."

        with self.assertRaisesRegex(ValidationError, msg):
            self._create_purchase(lot=wrong_lot, product=self.product)

    def test_03_onchange_product_clears_mismatched_lot(self):
        lot = self._create_lot("PO-ONCHANGE-LOT", product=self.product)
        purchase = self.env["purchase.order"].create({"partner_id": self.vendor.id})
        line = self.env["purchase.order.line"].new(
            {
                "order_id": purchase.id,
                "name": self.product.display_name,
                "product_id": self.product.id,
                "product_qty": 1.0,
                "product_uom_id": self.product.uom_id.id,
                "price_unit": 10.0,
                "date_planned": fields.Datetime.now(),
                "lot_id": lot.id,
            }
        )

        line.product_id = self.other_product
        line._onchange_product_id_clear_lot_id()

        self.assertFalse(line.lot_id)

