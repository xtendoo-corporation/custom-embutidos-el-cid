import io
import zipfile
import base64
from odoo import models, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_print_unidades_separadas(self):
        # Obtener el nombre del repartidor si es común a todos
        repartidor_name = ""
        if self:
            repartidores = self.mapped('repartidor_empleado_id.name')
            # Si todos tienen el mismo repartidor, usar su nombre
            if len(set(repartidores)) == 1 and repartidores[0]:
                repartidor_name = f'_{repartidores[0]}'.replace(' ', '_')

        # Generar los reportes para TODOS los registros seleccionados a la vez
        report_pesado = self.env.ref('embutidos_distribuitor_units.action_report_sale_order_unidades_pesadas')
        report_no_pesado = self.env.ref('embutidos_distribuitor_units.action_report_sale_order_unidades_no_pesadas')

        # Generar un único PDF de Pesados para todo el conjunto de pedidos
        pdf_pesado, _ = report_pesado._render_qweb_pdf('embutidos_distribuitor_units.action_report_sale_order_unidades_pesadas', res_ids=self.ids)

        # Generar un único PDF de No Pesados para todo el conjunto de pedidos
        pdf_no_pesado, _ = report_no_pesado._render_qweb_pdf('embutidos_distribuitor_units.action_report_sale_order_unidades_no_pesadas', res_ids=self.ids)

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

        attachment = self.env['ir.attachment'].create({
            'name': zip_name,
            'type': 'binary',
            'datas': base64.b64encode(zip_content),
            'mimetype': 'application/zip',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
