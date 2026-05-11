from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestSaleOrderPickingAllDone(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product_delivery_all = cls.env.ref("product.product_delivery_01")
        cls.product_delivery_all.invoice_policy = "delivery"
        cls.product_delivery_all.taxes_id = [Command.clear()]
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_delivery_all, cls.warehouse.lot_stock_id, 20.0
        )

    def _create_sale_order(self, qty=2.0):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_delivery_all.id,
                            "product_uom_qty": qty,
                        }
                    ),
                ],
            }
        )

    def test_confirm_and_delivery(self):
        sale_order = self._create_sale_order()

        sale_order.action_sale_order_confirm_and_delivery()

        self.assertEqual(sale_order.state, "sale")
        self.assertTrue(sale_order.picking_ids)
        self.assertTrue(all(p.state == "done" for p in sale_order.picking_ids))

    def test_confirm_and_invoice(self):
        sale_order = self._create_sale_order()

        action = sale_order.action_sale_order_confirm_and_invoice()

        self.assertEqual(sale_order.state, "sale")
        self.assertTrue(sale_order.invoice_ids)
        self.assertEqual(sale_order.invoice_ids.state, "draft")
        self.assertEqual(action.get("res_model"), "account.move")

    def test_delivery_from_confirmed_order(self):
        sale_order = self._create_sale_order()
        sale_order.action_confirm()

        sale_order.action_sale_order_delivery()

        self.assertTrue(sale_order.picking_ids)
        self.assertTrue(all(p.state == "done" for p in sale_order.picking_ids))

