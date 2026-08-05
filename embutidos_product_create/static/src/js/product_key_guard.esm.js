import { patch } from '@web/core/utils/patch';
import { rpc } from '@web/core/network/rpc';
import { FormController } from '@web/views/form/form_controller';
import { ProductKeyDialog } from '@embutidos_product_create/js/components/product_key_dialog';
import { ListController } from '@web/views/list/list_controller';
// Small helper that asks for the key by opening the existing server-side
// transient wizard (`embutidos.product.key.wizard`) in a modal. The wizard
// validates the key on the server and, on success, sets a temporary unlock
// for the user. After the modal closes we re-check the server; if the user
// is unlocked we return true, otherwise undefined (treated as cancel).
async function askKeyUsingDialog(env, message) {
    return new Promise((resolve) => {
        try {
            env.services.dialog.add(ProductKeyDialog, {
                title: message || 'Introduzca la clave',
                placeholder: '',
                startingValue: '',
                getPayload: (value) => resolve(value),
            }, {
                onClose: () => resolve(),
            });
        } catch (e) {
            console.error('embutidos_product_create: failed to open product key dialog', e);
            resolve();
        }
    });
    // If we reached here without returning the key, treat as cancelled
    return;
}

// Patch FormController to ask for the key before saving product records
patch(FormController.prototype, {
    async onWillSaveRecord(record) {
        // Call super implementation if any
        if (typeof super.onWillSaveRecord === 'function') {
            const res = await super.onWillSaveRecord(...arguments);
            if (res === false) {
                return false;
            }
        }
        const model = this.model?.root?.resModel || null;
        if (model === 'product.product' || model === 'product.template') {
            try {
                const needs = await rpc('/embutidos/product/needs_key');
                if (needs && needs.needs_key) {
                    const key = await askKeyUsingDialog(this.env, 'Introduzca la clave de modificación/creación de producto:');
                    if (!key) {
                        // user cancelled or validation failed -> abort save
                        return false;
                    }
                    // inject the validated key into the model config context so
                    // the upcoming RPC create/write will include it in env.context
                    this.model.config.context = Object.assign({}, this.model.config.context || {}, { product_key: key });
                }
            } catch (e) {
                // On RPC errors, let the save proceed and server will handle validation
                console.error('embutidos_product_create: error checking needs_key', e);
            }
        }
    },
});

// Patch ListController to handle inline edits / list saves similarly
patch(ListController.prototype, {
    async onWillSaveRecord(record) {
        if (typeof super.onWillSaveRecord === 'function') {
            const res = await super.onWillSaveRecord(...arguments);
            if (res === false) {
                return false;
            }
        }
        const model = this.model?.root?.resModel || null;
        if (model === 'product.product' || model === 'product.template') {
            try {
                const needs = await rpc('/embutidos/product/needs_key');
                if (needs && needs.needs_key) {
                    const key = await askKeyUsingDialog(this.env, 'Introduzca la clave de modificación/creación de producto:');
                    if (!key) {
                        return false;
                    }
                    this.model.config.context = Object.assign({}, this.model.config.context || {}, { product_key: key });
                }
            } catch (e) {
                console.error('embutidos_product_create: error checking needs_key', e);
            }
        }
    },
});

