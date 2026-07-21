# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _process_picking_validation_action(self, action):
        res_model = action.get("res_model")
        context = action.get("context", {})
        if not res_model:
            return True
        wizard = self.env[res_model].with_context(context).create({})
        if hasattr(wizard, "process_cancel_backorder"):
            return wizard.process_cancel_backorder()
        if hasattr(wizard, "process"):
            return wizard.process()
        return True

    def _process_delivery_pickings(self):
        for order in self:
            pickings = order.picking_ids.filtered(
                lambda p: p.state not in ("done", "cancel")
            )
            for picking in pickings:
                if picking.state == "draft":
                    picking.action_confirm()
                if picking.state in ("waiting", "confirmed", "partially_available"):
                    picking.action_assign()
                for move in picking.move_ids.filtered(
                    lambda m: m.state not in ("done", "cancel")
                ):
                    move.quantity = move.product_uom_qty
                    move.picked = True
                action = picking.with_context(skip_backorder=True).button_validate()
                if isinstance(action, dict):
                    order._process_picking_validation_action(action)
        return True

    def action_sale_order_confirm_and_delivery(self):
        orders_to_confirm = self.filtered(lambda so: so.state in ("draft", "sent"))
        if orders_to_confirm:
            orders_to_confirm.action_confirm()
        self._process_delivery_pickings()
        return True

    def action_sale_order_confirm_and_invoice(self):
        if not self.partner_id.show_sale_buttons:
            raise UserError(_("Este cliente no factura directo, usa el botón 'Confirmar y entregar'"))
        self.action_sale_order_confirm_and_delivery()
        invoices = self._create_invoices()
        return self.action_view_invoice(invoices=invoices)


    # Pedido confirmado( ya es un pedido de ventas)

    def action_sale_order_delivery(self):
        self._process_delivery_pickings()
        return True

    def action_sale_order_delivery_and_invoiced(self):
        self.action_sale_order_delivery()
        invoices = self._create_invoices()
        return self.action_view_invoice(invoices=invoices)
