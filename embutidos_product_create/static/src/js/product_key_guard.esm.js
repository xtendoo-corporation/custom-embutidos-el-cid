import { patch } from '@web/core/utils/patch';
import { rpc } from '@web/core/network/rpc';
import { FormController } from '@web/views/form/form_controller';
import { ProductKeyDialog } from '@embutidos_product_create/js/components/product_key_dialog';
import { ListController } from '@web/views/list/list_controller';
// Small helper that asks for the key in a modal dialog.
// The key is validated on the server during create/write.
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
}

function getRecordTarget(record) {
    const isCreate = record?.isNew === true;
    const candidateId = record?.resId ?? record?.data?.id ?? null;
    const numericId = Number(candidateId);
    const resId = Number.isInteger(numericId) && numericId > 0 ? numericId : null;
    return {
        resId,
        isCreate: isCreate || !resId,
    };
}

function resetProductKeyContext(controller) {
    const baseContext = Object.assign({}, controller.model?.config?.context || {});
    delete baseContext.product_key;
    delete baseContext.product_key_model_name;
    delete baseContext.product_key_record_id;
    delete baseContext.product_key_is_create;
    controller.model.config.context = baseContext;
    return baseContext;
}

async function validateKeyForTarget(model, resId, isCreate, key) {
    return rpc('/embutidos/product/validate_key', {
        model_name: model,
        res_id: resId,
        is_create: isCreate,
        key,
    });
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
                const { resId, isCreate } = getRecordTarget(record);
                resetProductKeyContext(this);
                const needs = await rpc('/embutidos/product/needs_key', {
                    model_name: model,
                    res_id: resId,
                    is_create: isCreate,
                });
                if (needs && needs.needs_key) {
                    const key = await askKeyUsingDialog(this.env, 'Introduzca la clave de modificación/creación de producto:');
                    if (!key) {
                        // user cancelled or validation failed -> abort save
                        return false;
                    }
                    const validation = await validateKeyForTarget(model, resId, isCreate, key);
                    if (!validation || !validation.valid) {
                        return false;
                    }
                }
            } catch (e) {
                // Fail closed: if guard RPC fails, do not continue with save.
                console.error('embutidos_product_create: error checking needs_key', e);
                return false;
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
                const { resId, isCreate } = getRecordTarget(record);
                resetProductKeyContext(this);
                const needs = await rpc('/embutidos/product/needs_key', {
                    model_name: model,
                    res_id: resId,
                    is_create: isCreate,
                });
                if (needs && needs.needs_key) {
                    const key = await askKeyUsingDialog(this.env, 'Introduzca la clave de modificación/creación de producto:');
                    if (!key) {
                        return false;
                    }
                    const validation = await validateKeyForTarget(model, resId, isCreate, key);
                    if (!validation || !validation.valid) {
                        return false;
                    }
                }
            } catch (e) {
                console.error('embutidos_product_create: error checking needs_key', e);
                return false;
            }
        }
    },
});

