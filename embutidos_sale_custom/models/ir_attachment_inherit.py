import logging
from odoo import models, api

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
	_inherit = 'ir.attachment'

	@api.model_create_multi
	def create(self, vals_list):
		_logger.debug('ir.attachment.create called with %s items', len(vals_list))
		records = super(IrAttachment, self).create(vals_list)
		try:
			for att in records:
				try:
					_logger.debug('Attachment created id=%s name=%s res_model=%s res_id=%s', att.id, att.name, att.res_model, att.res_id)
					if att.res_model == 'sale.order' and att.res_id:
						name = (att.name or '').lower()
						if any(pat in name for pat in ('unidades', 'unidades_pedidos', 'unidades_pesar', 'unidades_no_pesado')):
							order = self.env['sale.order'].browse(att.res_id)
							if order.exists():
								order.write({'impreso_unidades': True})
								_logger.info('Marked sale.order %s as impreso_unidades due to attachment %s', att.res_id, att.name)
				except Exception:
					_logger.exception('Error processing attachment id=%s name=%s', getattr(att, 'id', None), getattr(att, 'name', None))
		except Exception:
			_logger.exception('Unexpected error in ir.attachment.create post-processing')
		return records


