from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    unidades = fields.Char(string="Unidades")
