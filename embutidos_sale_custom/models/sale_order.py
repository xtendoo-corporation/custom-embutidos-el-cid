import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


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
    impreso_unidades = fields.Boolean(
        string="Impreso Unidades (Separado)",
        copy=False,
        readonly=True,
        help="Indica si se ejecutó la acción 'Unidades por Pedido (Separados)' para este pedido",
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

    def action_print_unidades_separadas(self):
        """
        Llamar a la implementación original (si existe) para generar el ZIP de 'Unidades por Pedido (Separados)'
        y marcar los pedidos como impresos (campo `impreso_unidades`).
        """
        _logger.info('action_print_unidades_separadas called for sale.order ids: %s', self.ids)
        # Llamamos a la implementación original si un módulo la provee
        result = False
        if hasattr(super(SaleOrder, self), 'action_print_unidades_separadas'):
            _logger.debug('Found super implementation for action_print_unidades_separadas, calling it')
            # Si el método original existe en otra clase, llamarlo
            result = super(SaleOrder, self).action_print_unidades_separadas()
            _logger.debug('Super implementation returned: %s', result)
        else:
            # Si no existe, intentamos ejecutar la acción servidor definida por XML
            action = self.env.ref('embutidos_distribuitor_units.action_server_report_sale_order_unidades', False)
            _logger.debug('Server action found: %s', bool(action))
            if action:
                # Ejecutar el código del servidor que invoca la generación
                # action is an ir.actions.server; calling _run_server_action will execute it
                for order in self:
                    _logger.debug('Running server action for order id %s', order.id)
                    action.with_context(active_id=order.id).run()
                result = True
                _logger.debug('Server action executed, result set True')

        # Si la generación tuvo éxito (o asumimos éxito), marcamos los pedidos
        try:
            # Marcamos solo los pedidos actuales
            self.write({'impreso_unidades': True})
        except Exception:
            # No queremos que falle la acción principal por un fallo al marcar el campo
            pass

        return result


