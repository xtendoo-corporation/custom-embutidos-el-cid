from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_weighed = fields.Boolean(
        string='¿Producto pesado?',
        help='Indica si el producto es pesado o no.'
    )

