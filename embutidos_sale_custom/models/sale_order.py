from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    repartidor_empleado_id = fields.Many2one(
        "hr.employee",
        string="Repartidor",
        required=True,
    )
    show_sale_buttons = fields.Boolean(
        related="partner_id.show_sale_buttons",
        string="Confirma, entregar y facturar activado",
    )

    def action_print_smart_report(self):
        self.ensure_one()
        # 1. Intentar obtener facturas a través de los campos estándar
        invoices = self.invoice_ids.filtered(
            lambda x: x.move_type == "out_invoice" and x.state != "cancel"
        )

        # 2. Fallback: Buscar a través de las líneas de factura vinculadas a las líneas de venta
        if not invoices:
            invoices = self.order_line.invoice_lines.move_id.filtered(
                lambda x: x.move_type == "out_invoice" and x.state != "cancel"
            )

        # 3. Fallback: Buscar por origen (matching con el nombre del pedido)
        if not invoices:
            invoices = self.env["account.move"].search([
                ("invoice_origin", "=", self.name),
                ("move_type", "=", "out_invoice"),
                ("state", "!=", "cancel"),
            ])

        if invoices:
            # Priorizamos las facturas publicadas ('posted') para imprimir
            posted_invoices = invoices.filtered(lambda x: x.state == "posted")
            # Si hay facturas publicadas, preferimos esas, si no, las que haya (draft etc)
            invoices_to_print = posted_invoices or invoices
            return self.env.ref("account.account_invoices").report_action(invoices_to_print)

        # Si no hay facturas, buscamos los albaranes
        pickings = self.picking_ids.filtered(lambda x: x.state != "cancel")
        if pickings:
            # Priorizamos albaranes finalizados
            done_pickings = pickings.filtered(lambda x: x.state == "done")
            picking_to_print = done_pickings or pickings
            # Usar 'action_report_delivery' (Vale de Entrega) en lugar de 'action_report_picking'
            return self.env.ref("stock.action_report_delivery").report_action(
                picking_to_print
            )

        return self.env.ref("sale.action_report_saleorder").report_action(self)
