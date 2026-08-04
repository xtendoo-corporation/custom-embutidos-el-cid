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
            # establecer desbloqueo temporal
            user._set_temp_unlock()
            return {'type': 'ir.actions.client', 'tag': 'reload'}
        raise UserError('Clave incorrecta.')

