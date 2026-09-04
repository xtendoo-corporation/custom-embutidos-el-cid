from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super()._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant)
        if self.restrict_lot_id and not vals.get("lot_id"):
            vals["lot_id"] = self.restrict_lot_id.id
            vals["lot_name"] = self.restrict_lot_id.name
        return vals
