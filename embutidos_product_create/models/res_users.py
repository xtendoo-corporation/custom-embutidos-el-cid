# -*- coding: utf-8 -*-
from odoo import models, fields
from datetime import timedelta


class ResUsers(models.Model):
    _inherit = 'res.users'

    allow_product_edit = fields.Boolean(string='Permitir crear/editar productos', default=False)
    product_key = fields.Char(string='Clave modificación/creación de producto')
    # Campo placeholder para compatibilidad con vistas externas que referencian printing_action
    printing_action = fields.Char(string='Printing Action')
    # Campo placeholder para compatibilidad con vistas que referencian printing_printer_id
    # Temporalmente lo dejamos como Char para evitar errores durante la carga del registro
    # (si instalas el módulo `base_report_to_printer` deberías cambiarlo a Many2one('printing.printer')).
    printing_printer_id = fields.Char(string='Printing Printer')
    _temp_product_unlocked = fields.Boolean(string='Desbloqueo temporal producto', default=False)
    _temp_product_unlocked_time = fields.Datetime(string='Tiempo desbloqueo temporal')

    def _validate_product_key(self, key):
        """
        Comprueba que la clave proporcionada coincide con la del usuario.
        """
        self.ensure_one()
        if not self.product_key:
            return False
        return bool(key and key == self.product_key)

    def _set_temp_unlock(self, minutes=2):
        """Activa un desbloqueo temporal para este usuario durante `minutes` minutos."""
        self.ensure_one()
        self._temp_product_unlocked = True
        self._temp_product_unlocked_time = fields.Datetime.now()
        return True

    def _clear_temp_unlock(self):
        self.ensure_one()
        self._temp_product_unlocked = False
        self._temp_product_unlocked_time = False
        return True

    def _check_temp_unlock_valid(self, minutes=2):
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
            return True
        # expirado
        self._clear_temp_unlock()
        return False
