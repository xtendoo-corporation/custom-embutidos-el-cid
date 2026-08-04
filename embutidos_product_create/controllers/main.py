from odoo import http


class EmbutidosProductController(http.Controller):
    # Usar 'jsonrpc' en Odoo 19 (type='json' está deprecado)
    @http.route('/embutidos/product/needs_key', type='jsonrpc', auth='user')
    def needs_key(self):
        user = http.request.env.user
        # Solo los usuarios con allow_product_edit True pueden modificar/crear productos
        needs = False
        try:
            if user.allow_product_edit and not user._check_temp_unlock_valid():
                needs = True
        except Exception:
            needs = False
        return {'needs_key': needs}

