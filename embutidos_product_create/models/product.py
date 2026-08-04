# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import AccessError


def _check_user_product_permissions(user, context_key_name='product_key'):
    """Helper: comprueba permisos para crear/editar productos para el usuario.
    - Si user.allow_product_edit False: lanza AccessError.
    - Si user.allow_product_edit True: comprueba desbloqueo temporal; si no está desbloqueado,
      busca en context[context_key_name] la clave y la compara con user.product_key.
    """
    # No hay bypass para superuser: solo los usuarios con la casilla marcada pueden crear/editar
    if not user.allow_product_edit:
        raise AccessError('No tiene permiso para crear o modificar productos.')
    # permitir si hay desbloqueo temporal válido
    if user._check_temp_unlock_valid():
        return True
    # buscar clave en context
    # Nota: los métodos create/write no reciben context directamente; en Odoo 19, env.context está disponible
    env = user.env
    ctx = env.context or {}
    key = ctx.get(context_key_name)
    if key and user._validate_product_key(key):
        # establecer desbloqueo temporal breve para permitir acciones subsecuentes inmediatas
        user._set_temp_unlock()
        return True
    raise AccessError('Es necesaria la clave de modificación/creación de producto.')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        user = self.env.user
        _check_user_product_permissions(user)
        record = super(ProductTemplate, self).create(vals)
        # limpiar desbloqueo temporal después de uso (evita reuso prolongado)
        try:
            if user._temp_product_unlocked:
                user._clear_temp_unlock()
        except Exception:
            pass
        return record

    def write(self, vals):
        user = self.env.user
        _check_user_product_permissions(user)
        res = super(ProductTemplate, self).write(vals)
        try:
            if user._temp_product_unlocked:
                user._clear_temp_unlock()
        except Exception:
            pass
        return res


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, vals):
        user = self.env.user
        _check_user_product_permissions(user)
        record = super(ProductProduct, self).create(vals)
        try:
            if user._temp_product_unlocked:
                user._clear_temp_unlock()
        except Exception:
            pass
        return record

    def write(self, vals):
        user = self.env.user
        _check_user_product_permissions(user)
        res = super(ProductProduct, self).write(vals)
        try:
            if user._temp_product_unlocked:
                user._clear_temp_unlock()
        except Exception:
            pass
        return res

