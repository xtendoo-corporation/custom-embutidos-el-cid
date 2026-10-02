import logging
from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_print_unidades_separadas(self):
        _logger.info('action_print_unidades_separadas called for sale.order ids: %s', self.ids)
        if not self:
            return False
        report_model = self.env['ir.actions.report']
        if not hasattr(report_model, 'print_document'):
            raise UserError(_("Se necesita el módulo base_report_to_printer para imprimir directamente."))

        # Un único informe de Pesados y otro de No Pesados para todo el conjunto,
        # enviados directamente a la cola de impresión (uno detrás de otro).
        reports = (
            self.env.ref('embutidos_distribuitor_units.action_report_sale_order_unidades_pesadas'),
            self.env.ref('embutidos_distribuitor_units.action_report_sale_order_unidades_no_pesadas'),
        )
        for report in reports:
            report.print_document(self.ids)
            _logger.info('Sent report %s to printer for sale.order ids: %s', report.report_name, self.ids)

        # Marcar los pedidos como impresos solo si el envío no falló.
        self.write({'impreso_unidades': True})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Unidades por Pedido"),
                'message': _("Enviados a la cola de impresión: Unidades Pesar y Unidades No Pesado."),
                'type': 'success',
            },
        }
