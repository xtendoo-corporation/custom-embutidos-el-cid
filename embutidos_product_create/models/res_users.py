# -*- coding: utf-8 -*-
from odoo import models, fields
from datetime import timedelta


class ResUsers(models.Model):
    _inherit = 'res.users'

    allow_product_edit = fields.Boolean(string='Permitir crear/editar productos', default=False)
    product_key = fields.Char(string='Clave modificación/creación de producto')

    _temp_product_unlocked = fields.Boolean(string='Desbloqueo temporal producto', default=False)
    _temp_product_unlocked_time = fields.Datetime(string='Tiempo desbloqueo temporal')
    _temp_product_target = fields.Char(string='Objetivo desbloqueo temporal producto')

    def _build_product_target_signature(self, model_name=None, record_ids=None, is_create=False):
        """Construye una firma estable del objetivo que se quiere modificar."""
        self.ensure_one()
        model = model_name or ''
        if is_create:
            return f'create:{model}'
        if not record_ids:
            return f'unknown:{model}'
        if isinstance(record_ids, int):
            ids = [record_ids]
        else:
            ids = [int(rec_id) for rec_id in record_ids if rec_id]
        ids = sorted(set(ids))
        ids_str = ','.join(str(rec_id) for rec_id in ids)
        return f'write:{model}:{ids_str}'

    def _validate_product_key(self, key):
        """
        Comprueba que la clave proporcionada coincide con la del usuario.
        """
        self.ensure_one()
        if not self.product_key:
            return False
        return bool(key and key == self.product_key)

    def _set_temp_unlock(self, target_signature=None):
        """Activa un desbloqueo temporal ligado al producto validado."""
        self.ensure_one()
        self._temp_product_unlocked = True
        self._temp_product_unlocked_time = fields.Datetime.now()
        self._temp_product_target = target_signature or False
        return True

    def _clear_temp_unlock(self):
        self.ensure_one()
        self._temp_product_unlocked = False
        self._temp_product_unlocked_time = False
        self._temp_product_target = False
        return True

    def _check_temp_unlock_valid(self, target_signature=None, minutes=10):
        self.ensure_one()
        if not self._temp_product_unlocked or not self._temp_product_unlocked_time:
            return False
        try:
            # convertir ambos a datetime para comparar
            dt = fields.Datetime.from_string(self._temp_product_unlocked_time)
            now_dt = fields.Datetime.from_string(fields.Datetime.now())
        except Exception:
            return False
        if (now_dt - dt) <= timedelta(minutes=minutes):
            if target_signature and self._temp_product_target != target_signature:
                return False
            return True
        # expirado
        self._clear_temp_unlock()
        return False
