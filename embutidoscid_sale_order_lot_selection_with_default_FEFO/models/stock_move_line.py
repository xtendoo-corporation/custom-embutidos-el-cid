# Copyright 2026 Daniel Domínguez (xtendoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    expiration_date = fields.Datetime(
        related="lot_id.expiration_date",
        string="Expiration Date",
        store=True,
        readonly=True,
        copy=False,
    )

