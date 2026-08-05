# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError


class ProductKeyWizard(models.TransientModel):
    _name = 'embutidos.product.key.wizard'
    _description = 'Validación de clave para creación/edición de producto'

    key = fields.Char(string='Clave', required=True)

    def action_validate(self):
        user = self.env.user
        if user._validate_product_key(self.key):
            # Set a short-lived temporary unlock for this user so the
            # immediate create/write RPC can proceed. The create/write
            # methods will clear this unlock after use. This enforces that
            # the user must enter the key for every separate create/write
            # operation (the unlock is not permanent).
            user._set_temp_unlock()
            return {'type': 'ir.actions.act_window_close'}
        raise UserError('Clave incorrecta.')

