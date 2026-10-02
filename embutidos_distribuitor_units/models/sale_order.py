import logging
from odoo import models

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_print_unidades_separadas(self):
        _logger.info('action_print_unidades_separadas called for sale.order ids: %s', self.ids)
        if not self:
            return False
        # Un único informe de Pesados y otro de No Pesados para todo el conjunto,
        # lanzados en cola desde el cliente (así funcionan QZ Tray, etc.).
        reports = (
            self.env.ref('embutidos_distribuitor_units.action_report_sale_order_unidades_pesadas'),
            self.env.ref('embutidos_distribuitor_units.action_report_sale_order_unidades_no_pesadas'),
        )
        jobs = [report.report_action(self) for report in reports]

        return {
            'type': 'ir.actions.client',
            'tag': 'embutidos_print_queue',
            'params': {'jobs': jobs},
        }
