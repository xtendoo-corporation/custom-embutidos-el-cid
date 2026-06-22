from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    unidades = fields.Integer(string="Unidades", default=0)
