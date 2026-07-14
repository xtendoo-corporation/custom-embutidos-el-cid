from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    unidades = fields.Char(string="Unidades")

    def _prepare_invoice_line(self, **optional_values):
        values = super()._prepare_invoice_line(**optional_values)
        values['unidades'] = self.unidades
        return values

    def _prepare_procurement_values(self):
        values = super()._prepare_procurement_values()
        values['unidades'] = self.unidades
        return values
