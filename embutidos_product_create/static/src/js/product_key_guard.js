odoo.define('@embutidos_product_create/js/product_key_guard', function (require) {
    'use strict';

    const BasicModel = require('web.BasicModel');
    const rpc = require('web.rpc');
    const { patch } = require('@web/core/utils/patch');
    const Dialog = require('web.Dialog');
    // Controllers (para parchear guardados desde UI con patch)
    let FormController;
    let ListController;
    try{
        FormController = require('web.FormController');
    }catch(e){}
    try{
        ListController = require('web.ListController');
    }catch(e){}

    // Helper: modal usando Dialog nativo de Odoo para pedir la clave
    function promptKey(message){
        return new Promise(function(resolve){
            // construir contenido con jQuery para el Dialog
            const $content = $('<div/>');
            const $title = $('<div/>').text(message || 'Introduzca la clave').css('margin-bottom','8px');
            const $input = $('<input/>').attr('type','password').css({width: '100%', boxSizing: 'border-box', marginBottom: '12px'});
            $content.append($title).append($input);
            const dialog = new Dialog(null, {
                title: message || 'Introduzca la clave',
                $content: $content,
                buttons: [
                    {text: 'Cancelar', classes: 'btn-secondary', close: true, click: function(){ resolve(null); }},
                    {text: 'Validar', classes: 'btn-primary', close: true, click: function(){ resolve($input.val()||''); }}
                ]
            });
            dialog.open();
            setTimeout(function(){ $input.focus(); }, 50);
        });
    }

    // Small helper to store a prevalidated key so BasicModel._rpc can pick it up
    function setTemporaryKey(key){
        try{
            window.__embutidos_product_key = key;
            setTimeout(function(){ try{ delete window.__embutidos_product_key; }catch(e){} }, 2*60*1000);
        }catch(e){}
    }

    // Nota: no se sobreescribe rpc.query globalmente en Odoo 19 para evitar
    // interferir con otros módulos. Usamos únicamente el patch de BasicModel
    // para interceptar las llamadas RPC generadas por el framework (forma OWL).

    // Patchear BasicModel para interceptar create/write sobre productos (cobertura amplia)
    patch(BasicModel.prototype, 'embutidos_product_create.BasicModel', {
        async _rpc(params, options) {
            try {
                const p = params || {};
                if (p.model && (p.model === 'product.product' || p.model === 'product.template') && (p.method === 'create' || p.method === 'write')) {
                    const res = await rpc.query({route: '/embutidos/product/needs_key'});
                    if (res && res.needs_key) {
                        // If a controller already set a temporary key, use it
                        if (window.__embutidos_product_key) {
                            const pre = window.__embutidos_product_key;
                            try{ delete window.__embutidos_product_key; }catch(e){}
                            p.kwargs = p.kwargs || {};
                            p.kwargs.context = Object.assign({}, p.kwargs.context || {}, {product_key: pre});
                        } else {
                            const key = await promptKey('Introduzca la clave de modificación/creación de producto:');
                            if (key === null) {
                                return Promise.reject(new Error('Operación cancelada por el usuario'));
                            }
                            p.kwargs = p.kwargs || {};
                            p.kwargs.context = Object.assign({}, p.kwargs.context || {}, {product_key: key});
                        }
                    }
                }
            } catch (err) {
                // Si el usuario canceló la entrada, propagamos la cancelación para
                // que la llamada RPC sea abortada en el cliente y no se envíe al servidor.
                if (err && err.message === 'Operación cancelada por el usuario') {
                    return Promise.reject(err);
                }
                // Para otros errores del prompt o del rpc, ignoramos y dejamos que
                // el servidor valide (no inyectamos la clave).
            }
            return this._super.apply(this, arguments);
        },
    });

    // Patch FormController to ask for the key before saving from the form UI
    if (FormController) {
        patch(FormController.prototype, 'embutidos_product_create.FormController', {
            async saveRecord(recordId) {
                try{
                    const modelName = this.modelName || (this.props && this.props.resModel) || null;
                    if (modelName && (modelName === 'product.product' || modelName === 'product.template')){
                        const res = await rpc.query({route: '/embutidos/product/needs_key'});
                        if (res && res.needs_key){
                            const key = await promptKey('Introduzca la clave de modificación/creación de producto:');
                            if (key === null){
                                return Promise.reject(new Error('Operación cancelada por el usuario'));
                            }
                            setTemporaryKey(key);
                        }
                    }
                }catch(err){
                    if (err && err.message === 'Operación cancelada por el usuario'){
                        return Promise.reject(err);
                    }
                }
                return this._super.apply(this, arguments);
            },
        });
    }

    // Patch ListController (for mass-edit/save from list views)
    if (ListController) {
        patch(ListController.prototype, 'embutidos_product_create.ListController', {
            async _save(records){
                try{
                    const modelName = this.modelName || (this.props && this.props.resModel) || null;
                    if (modelName && (modelName === 'product.product' || modelName === 'product.template')){
                        const res = await rpc.query({route: '/embutidos/product/needs_key'});
                        if (res && res.needs_key){
                            const key = await promptKey('Introduzca la clave de modificación/creación de producto:');
                            if (key === null){
                                return Promise.reject(new Error('Operación cancelada por el usuario'));
                            }
                            setTemporaryKey(key);
                        }
                    }
                }catch(err){
                    if (err && err.message === 'Operación cancelada por el usuario'){
                        return Promise.reject(err);
                    }
                }
                return this._super.apply(this, arguments);
            },
        });
    }

});


