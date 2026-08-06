# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import AccessError


def _is_module_loading_context(user):
    """Evita bloquear writes técnicos durante carga/actualización de módulos."""
    ctx = user.env.context or {}
    return bool(ctx.get('install_mode') or ctx.get('module'))


def _is_internal_guard_bypass_context(user):
    """Permite operaciones internas lanzadas tras validar en product.template."""
    ctx = user.env.context or {}
    return bool(ctx.get('embutidos_product_guard_bypass'))


def _check_user_product_permissions(
    user,
    model_name,
    record_ids=None,
    is_create=False,
    context_key_name='product_key',
):
    """Helper: comprueba permisos para crear/editar productos para el usuario.
    - Si user.allow_product_edit False: lanza AccessError.
    - Si user.allow_product_edit True: comprueba desbloqueo temporal; si no está desbloqueado,
      busca en context[context_key_name] la clave y la compara con user.product_key.
    """
    if _is_module_loading_context(user):
        return True
    if _is_internal_guard_bypass_context(user):
        return True
    # No hay bypass para superuser: solo los usuarios con la casilla marcada pueden crear/editar
    if not user.allow_product_edit:
        raise AccessError('No tiene permiso para crear o modificar productos.')
    target_signature = user._build_product_target_signature(
        model_name=model_name,
        record_ids=record_ids,
        is_create=is_create,
    )
    # Si ya se validó para este objetivo, permitir operación sin volver a pedir clave.
    if user._check_temp_unlock_valid(target_signature=target_signature):
        return True
    # buscar clave en context
    # Nota: los métodos create/write no reciben context directamente; en Odoo 19, env.context está disponible
    env = user.env
    ctx = env.context or {}
    key = ctx.get(context_key_name)
    key_model_name = ctx.get('product_key_model_name')
    key_record_id = ctx.get('product_key_record_id')
    key_is_create = bool(ctx.get('product_key_is_create'))
    context_signature = user._build_product_target_signature(
        model_name=key_model_name,
        record_ids=[key_record_id] if key_record_id else None,
        is_create=key_is_create,
    )
    if key and user._validate_product_key(key) and context_signature == target_signature:
        user._set_temp_unlock(target_signature=target_signature)
        return True
    raise AccessError('Es necesaria la clave de modificación/creación de producto.')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        user = self.env.user
        _check_user_product_permissions(user, model_name=self._name, is_create=True)
        record = super(ProductTemplate, self.with_context(embutidos_product_guard_bypass=True)).create(vals)
        user._set_temp_unlock(
            target_signature=user._build_product_target_signature(
                model_name=self._name,
                record_ids=record.ids,
            )
        )
        return record

    def write(self, vals):
        user = self.env.user
        _check_user_product_permissions(user, model_name=self._name, record_ids=self.ids)
        res = super(ProductTemplate, self.with_context(embutidos_product_guard_bypass=True)).write(vals)
        if len(self.ids) == 1:
            user._set_temp_unlock(
                target_signature=user._build_product_target_signature(
                    model_name=self._name,
                    record_ids=self.ids,
                )
            )
        return res


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, vals):
        user = self.env.user
        _check_user_product_permissions(user, model_name=self._name, is_create=True)
        record = super(ProductProduct, self).create(vals)
        user._set_temp_unlock(
            target_signature=user._build_product_target_signature(
                model_name=self._name,
                record_ids=record.ids,
            )
        )
        return record

    def write(self, vals):
        user = self.env.user
        _check_user_product_permissions(user, model_name=self._name, record_ids=self.ids)
        res = super(ProductProduct, self).write(vals)
        if len(self.ids) == 1:
            user._set_temp_unlock(
                target_signature=user._build_product_target_signature(
                    model_name=self._name,
                    record_ids=self.ids,
                )
            )
        return res

