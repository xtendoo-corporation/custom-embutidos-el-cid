# Copyright 2026 Daniel Domínguez (xtendoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    lot_id = fields.Many2one(
        "stock.lot",
        string="Lote",
        domain="[('product_id', '=', product_id), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        copy=False,
        store=True,
        readonly=False,
        check_company=True,
        compute="_compute_lot_id",
    )
    expiration_date = fields.Datetime(
        related="lot_id.expiration_date",
        string="Caducidad",
        store=True,
        readonly=True,
        copy=False,
    )

    @api.depends('sale_line_ids', 'sale_line_ids.move_ids', 'sale_line_ids.move_ids.lot_ids',
                 'purchase_line_id', 'purchase_line_id.move_ids', 'purchase_line_id.move_ids.lot_ids',
                 'product_id')
    def _compute_lot_id(self):
        """Obtener el lote automáticamente desde los movimientos de stock relacionados"""
        for line in self:
            if not line.product_id or line.display_type in ('line_section', 'line_note'):
                line.lot_id = False
                continue

            # Si ya tiene un lote asignado manualmente, lo respetamos
            if line.lot_id and line.lot_id.product_id == line.product_id:
                continue

            lot = False

            # Buscar desde líneas de pedido de venta
            if line.sale_line_ids:
                for sale_line in line.sale_line_ids:
                    # Primero intentar desde el lote directo de la línea de venta
                    if hasattr(sale_line, 'lot_id') and sale_line.lot_id:
                        lot = sale_line.lot_id
                        break
                    # Buscar en los movimientos de stock relacionados
                    for move in sale_line.move_ids.filtered(lambda m: m.state == 'done'):
                        if move.restrict_lot_id:
                            lot = move.restrict_lot_id
                            break
                        # Buscar en las líneas de movimiento
                        for move_line in move.move_line_ids.filtered(lambda ml: ml.lot_id):
                            lot = move_line.lot_id
                            break
                        if lot:
                            break
                    if lot:
                        break

            # Buscar desde línea de pedido de compra
            elif line.purchase_line_id:
                purchase_line = line.purchase_line_id
                # Primero intentar desde el lote directo de la línea de compra
                if hasattr(purchase_line, 'lot_id') and purchase_line.lot_id:
                    lot = purchase_line.lot_id
                else:
                    # Buscar en los movimientos de stock relacionados
                    for move in purchase_line.move_ids.filtered(lambda m: m.state == 'done'):
                        if move.restrict_lot_id:
                            lot = move.restrict_lot_id
                            break
                        # Buscar en las líneas de movimiento
                        for move_line in move.move_line_ids.filtered(lambda ml: ml.lot_id):
                            lot = move_line.lot_id
                            break
                        if lot:
                            break

            line.lot_id = lot if lot else False

    @api.onchange("product_id")
    def _onchange_product_id_clear_lot_id(self):
        for line in self:
            if line.lot_id and line.lot_id.product_id != line.product_id:
                line.lot_id = False

