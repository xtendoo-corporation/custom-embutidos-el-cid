from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_approve(self, force=False):
        result = super().button_approve(force=force)
        self._process_receipt_pickings()
        return result

    def _process_receipt_pickings(self):
        for order in self:
            pickings = order.picking_ids.filtered(lambda p: p.state not in ("done", "cancel"))
            for picking in pickings:
                if picking.state == "draft":
                    picking.action_confirm()
                if picking.state in ("waiting", "confirmed", "partially_available"):
                    picking.action_assign()
                for move in picking.move_ids.filtered(lambda m: m.state not in ("done", "cancel")):
                    move.quantity = move.product_uom_qty
                    move.picked = True
                action = picking.with_context(skip_backorder=True).button_validate()
                if isinstance(action, dict):
                    order._process_picking_validation_action(action)
        return True

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
