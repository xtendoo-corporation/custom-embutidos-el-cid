from odoo import http


class EmbutidosProductController(http.Controller):
    def _normalize_target(self, model_name=None, res_id=None, is_create=False):
        normalized_model = model_name or False
        normalized_is_create = bool(is_create)
        normalized_res_id = False
        if not normalized_is_create and res_id:
            try:
                res_id_int = int(res_id)
                normalized_res_id = res_id_int if res_id_int > 0 else False
            except Exception:
                normalized_res_id = False
        return normalized_model, normalized_res_id, normalized_is_create

    # Usar 'jsonrpc' en Odoo 19 (type='json' está deprecado)
    @http.route('/embutidos/product/needs_key', type='jsonrpc', auth='user')
    def needs_key(self, model_name=None, res_id=None, is_create=False):
        user = http.request.env.user
        # Solo los usuarios con allow_product_edit True pueden modificar/crear productos
        needs = False
        try:
            if user.allow_product_edit:
                model_name, res_id, is_create = self._normalize_target(model_name, res_id, is_create)
                target_signature = user._build_product_target_signature(
                    model_name=model_name,
                    record_ids=[res_id] if res_id else None,
                    is_create=is_create,
                )
                if is_create:
                    needs = True
                else:
                    needs = not user._check_temp_unlock_valid(target_signature=target_signature)
            else:
                needs = False
        except Exception:
            needs = False
        return {'needs_key': needs}

    @http.route('/embutidos/product/validate_key', type='jsonrpc', auth='user')
    def validate_key(self, key=None, model_name=None, res_id=None, is_create=False):
        user = http.request.env.user
        if not user.allow_product_edit:
            return {'valid': False, 'message': 'No tiene permiso para crear o modificar productos.'}
        model_name, res_id, is_create = self._normalize_target(model_name, res_id, is_create)
        target_signature = user._build_product_target_signature(
            model_name=model_name,
            record_ids=[res_id] if res_id else None,
            is_create=is_create,
        )
        if not key or not user._validate_product_key(key):
            return {'valid': False, 'message': 'Clave incorrecta.'}
        user._set_temp_unlock(target_signature=target_signature)
        return {'valid': True}

