odoo.define('embutidos_product_create.product_key_guard', function (require) {
    'use strict';

    const BasicModel = require('web.BasicModel');
    const rpc = require('web.rpc');
    const { patch } = require('@web/core/utils/patch');

    // Patchear BasicModel para interceptar create/write sobre productos (cobertura amplia)
    patch(BasicModel.prototype, 'embutidos_product_create.BasicModel', {
        async _rpc(params, options) {
            try {
                const p = params || {};
                if (p.model && (p.model === 'product.product' || p.model === 'product.template') && (p.method === 'create' || p.method === 'write')) {
                    const res = await rpc.query({route: '/embutidos/product/needs_key'});
                    if (res && res.needs_key) {
                        const key = window.prompt('Introduzca la clave de modificación/creación de producto:');
                        if (key === null) {
                            throw new Error('Operación cancelada por el usuario');
                        }
                        p.kwargs = p.kwargs || {};
                        p.kwargs.context = Object.assign({}, p.kwargs.context || {}, {product_key: key});
                    }
                }
            } catch (err) {
                // ignorar: permitimos que la llamada original siga y el servidor valide
            }
            return this._super.apply(this, arguments);
        },
    });
});


