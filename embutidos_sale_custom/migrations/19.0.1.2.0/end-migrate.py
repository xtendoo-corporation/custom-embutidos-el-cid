from odoo import api, SUPERUSER_ID
from odoo.addons.embutidos_sale_custom.hooks import migrate_repartidor_empleado_field


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    migrate_repartidor_empleado_field(env)
