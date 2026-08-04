import io
import zipfile
import base64
import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_print_unidades_separadas(self):
        _logger.info('action_print_unidades_separadas called for sale.order ids: %s', self.ids)
        # Obtener el nombre del repartidor si es común a todos
        repartidor_name = ""
        if self:
            repartidores = self.mapped('repartidor_empleado_id.name')
            # Si todos tienen el mismo repartidor, usar su nombre
            if len(set(repartidores)) == 1 and repartidores[0]:
                repartidor_name = f'_{repartidores[0]}'.replace(' ', '_')
        _logger.debug('repartidor_name determined: %s', repartidor_name)

        # Generar los reportes para TODOS los registros seleccionados a la vez
        report_pesado = self.env.ref('embutidos_distribuitor_units.action_report_sale_order_unidades_pesadas')
        report_no_pesado = self.env.ref('embutidos_distribuitor_units.action_report_sale_order_unidades_no_pesadas')

        # Generar un único PDF de Pesados para todo el conjunto de pedidos
        pdf_pesado, _ = report_pesado._render_qweb_pdf('embutidos_distribuitor_units.action_report_sale_order_unidades_pesadas', res_ids=self.ids)
        _logger.info('Rendered pdf_pesado for sale.order ids: %s (size=%s)', self.ids, len(pdf_pesado) if pdf_pesado else 0)

        # Generar un único PDF de No Pesados para todo el conjunto de pedidos
        pdf_no_pesado, _ = report_no_pesado._render_qweb_pdf('embutidos_distribuitor_units.action_report_sale_order_unidades_no_pesadas', res_ids=self.ids)
        _logger.info('Rendered pdf_no_pesado for sale.order ids: %s (size=%s)', self.ids, len(pdf_no_pesado) if pdf_no_pesado else 0)

        # Crear ZIP en memoria con solo dos archivos
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f'Unidades_PESAR_Global{repartidor_name}.pdf', pdf_pesado)
            zip_file.writestr(f'Unidades_NO_pesado_Global{repartidor_name}.pdf', pdf_no_pesado)

        zip_buffer.seek(0)
        zip_content = zip_buffer.read()
        zip_buffer.close()

        # Nombre del ZIP genérico o basado en el primer pedido, incluyendo repartidor
        zip_name = f'Unidades_Pedidos{repartidor_name}.zip' if len(self) > 1 else f'Unidades_{self[0].name}{repartidor_name}.zip'
        _logger.info('Creating attachment with name: %s for sale.order ids: %s', zip_name, self.ids)

        attachment = self.env['ir.attachment'].create({
            'name': zip_name,
            'type': 'binary',
            'datas': base64.b64encode(zip_content),
            'mimetype': 'application/zip',
        })
        _logger.info('Attachment created id=%s name=%s', attachment.id, attachment.name)

        # Marcar los pedidos como impresos. Se coloca después de la creación del attachment.
        try:
            self.write({'impreso_unidades': True})
            _logger.info('Marked sale.order ids as impreso_unidades: %s', self.ids)
        except Exception as e:
            _logger.exception('Failed to write impreso_unidades on sale.order ids %s: %s', self.ids, e)

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

