import logging
import re
from odoo import models

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    """Interceptar la acción de impresión de informes para marcar los pedidos
    relacionados como 'impreso_unidades'.

    Esto cubre impresiones realizadas sobre los modelos: sale.order, stock.picking
    y account.move (facturas). Se hace en este módulo personalizado para no
    tocar código core.
    """

    _inherit = "ir.actions.report"

    def report_action(self, *args, **kwargs):
        # Llamar primero a la implementación original usando la firma que toque
        result = None
        try:
            result = super(IrActionsReport, self).report_action(*args, **kwargs)
        except Exception:
            # No queremos bloquear la impresión por nuestro hook; loguear y seguir
            _logger.debug('Fallo al llamar a super().report_action, pero continuamos para intentar marcar pedidos', exc_info=True)

        # Intentar determinar los ids pasados y marcar los pedidos relacionados
        try:
            # Extraer res_ids desde kwargs o desde args (si existe en la primera posición)
            res_ids = kwargs.get('res_ids') if 'res_ids' in kwargs else (args[0] if len(args) > 0 else None)
            # Normalizar a lista de ids. Puede venir como int, list de ids, o recordset
            _res_ids = []
            if res_ids is None:
                _res_ids = []
            else:
                # Si es recordset (tiene .ids), obtener ids
                try:
                    if hasattr(res_ids, 'ids'):
                        _res_ids = list(res_ids.ids)
                    elif isinstance(res_ids, (int,)):
                        _res_ids = [res_ids]
                    else:
                        # Asumir iterable de ids
                        _res_ids = list(res_ids)
                except Exception:
                    # Fallback: convertir a lista si posible
                    try:
                        _res_ids = list(res_ids)
                    except Exception:
                        _res_ids = []

            # Si no hay ids explícitos, intentar extraer active_id(s) desde el contexto
            if not _res_ids:
                try:
                    ctx = kwargs.get('context') or self.env.context
                    if isinstance(ctx, dict):
                        active = ctx.get('active_ids') or ctx.get('active_id')
                    else:
                        # ctx puede venir como recordset/context object
                        active = self.env.context.get('active_ids') or self.env.context.get('active_id')
                    if active:
                        if isinstance(active, (int,)):
                            _res_ids = [active]
                        else:
                            _res_ids = list(active)
                except Exception:
                    _logger.debug('No se pudo extraer active_id(s) desde el context')

            for report in self:
                model_name = getattr(report, 'model', False)
                # Loguear información detallada para depuración
                try:
                    _logger.debug('report_action called: report_id=%s report_name=%s report_model=%s res_ids=%r args_type=%s kwargs_keys=%s',
                                  report.id, getattr(report, 'report_name', None), model_name, res_ids,
                                  type(res_ids), list(kwargs.keys()))
                except Exception:
                    _logger.debug('report_action called for report record, pero fallo al loguear detalles')

                if not model_name or not _res_ids:
                    _logger.debug('Skipping report %s because no model or no ids resolved (model=%s ids=%s)', getattr(report, 'id', None), model_name, _res_ids)
                    continue

                # Obtener records del modelo para los ids indicados
                try:
                    records = self.env[model_name].browse(_res_ids)
                except Exception:
                    _logger.debug('No se pudieron obtener registros para model %s ids %s', model_name, _res_ids)
                    continue

                # Resolver pedidos de venta relacionados según el modelo
                orders = self._resolve_sale_orders_from_records(model_name, records)
                if orders:
                    try:
                        orders.write({'impreso_unidades': True})
                        _logger.info('Marcados impreso_unidades para pedidos: %s (report_id=%s)', orders.ids, getattr(report, 'id', None))
                    except Exception:
                        _logger.exception('Error marcando impreso_unidades para pedidos: %s', orders.ids if orders else [])
                else:
                    _logger.debug('No se encontraron sale.order relacionados para report %s ids %s', getattr(report, 'id', None), _res_ids)

        except Exception:
            _logger.exception('Error procesando report_action para marcar impreso_unidades')

        return result

    def render_qweb_pdf(self, docids, data=None):
        """Interceptar renderizado directo a PDF (si algún código llama al método
        para generar el PDF) y marcar los pedidos relacionados.
        """
        # Llamar a la implementación original
        result = None
        try:
            result = super(IrActionsReport, self).render_qweb_pdf(docids, data=data)
        except Exception:
            _logger.debug('Fallo al llamar a super().render_qweb_pdf, continuamos para intentar marcar pedidos', exc_info=True)

        # Normalizar docids a lista de ids
        _docids = []
        try:
            if docids is None:
                _docids = []
            elif hasattr(docids, 'ids'):
                _docids = list(docids.ids)
            elif isinstance(docids, (int,)):
                _docids = [docids]
            else:
                _docids = list(docids)
        except Exception:
            try:
                _docids = list(docids)
            except Exception:
                _docids = []

        try:
            for report in self:
                model_name = getattr(report, 'model', False)
                if not model_name or not _docids:
                    continue
                try:
                    records = self.env[model_name].browse(_docids)
                except Exception:
                    _logger.debug('No se pudieron obtener registros para model %s ids %s', model_name, _docids)
                    continue

                orders = self._resolve_sale_orders_from_records(model_name, records)
                if orders:
                    try:
                        orders.write({'impreso_unidades': True})
                        _logger.debug('Marcados impreso_unidades para pedidos (render_qweb_pdf): %s', orders.ids)
                    except Exception:
                        _logger.exception('Error marcando impreso_unidades para pedidos (render_qweb_pdf): %s', orders.ids if orders else [])
        except Exception:
            _logger.exception('Error procesando render_qweb_pdf para marcar impreso_unidades')

        return result

    def _resolve_sale_orders_from_records(self, model_name, records):
        """Dado un conjunto de records de distintos modelos, devolver los
        sale.order relacionados (puede devolver un recordset vacío).
        """
        SaleOrder = self.env['sale.order']

        if model_name == 'sale.order':
            return records

        if model_name == 'stock.picking':
            # stock.picking.sale_id
            orders = records.mapped('sale_id')
            # Fallback: buscar por origin (nombre del pedido) si no hay sale_id
            if not orders:
                for p in records:
                    try:
                        if getattr(p, 'origin', False):
                            so = SaleOrder.search([('name', '=', p.origin)], limit=1)
                            if so:
                                orders |= so
                    except Exception:
                        _logger.debug('Error buscando sale.order por origin para picking %s', getattr(p, 'id', False))
            return orders

        if model_name == 'account.move':
            # Primero, vía líneas: invoice_line_ids -> sale_line_ids -> order_id
            orders = records.mapped('invoice_line_ids.sale_line_ids.order_id')
            # Fallback: buscar por invoice_origin (nombre del pedido). invoice_origin puede contener varios orígenes.
            for inv in records:
                try:
                    origin = (inv.invoice_origin or '')
                    if origin:
                        # Separar por delimitadores comunes y buscar coincidencias exactas o similares
                        tokens = [t.strip() for t in re.split('[,;/|]', origin) if t.strip()]
                        for tok in tokens:
                            # Buscar coincidencia exacta primero
                            so = SaleOrder.search([('name', '=', tok)], limit=1)
                            if not so:
                                # Fallback: buscar por token dentro del name
                                so = SaleOrder.search([('name', 'ilike', tok)], limit=1)
                            if so:
                                orders |= so
                except Exception:
                    # Ignorar cualquier problema al buscar
                    _logger.debug('Error buscando sale.order por invoice_origin para invoice %s', getattr(inv, 'id', False))
            return orders

        # Otros modelos: intentar mapear por sale_id si existe
        try:
            return records.mapped('sale_id')
        except Exception:
            return SaleOrder.browse()

