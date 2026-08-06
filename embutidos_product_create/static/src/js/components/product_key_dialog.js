import { Component, useState } from '@odoo/owl';
import { Dialog } from '@web/core/dialog/dialog';

// Lightweight OWL component used as dialog content. The template is
// provided in `static/src/xml/product_key_dialog.xml` (t-name "embutidos.ProductKeyDialog").
export class ProductKeyDialog extends Component {
    static template = 'embutidos.ProductKeyDialog';
    static components = { Dialog };

    setup() {
        this.state = useState({ value: this.props.startingValue || '' });
        // Called by the template when user confirms
        this._confirm = () => {
            try {
                if (this.props.getPayload) {
                    this.props.getPayload(this.state.value);
                }
            } finally {
                // close the dialog if dialogData exists
                if (this.env.dialogData && this.env.dialogData.close) {
                    this.env.dialogData.close();
                }
            }
        };
        this._cancel = () => {
            if (this.props.getPayload) {
                this.props.getPayload(undefined);
            }
            if (this.env.dialogData && this.env.dialogData.close) {
                this.env.dialogData.close();
            }
        };
        this._onKeydown = (ev) => {
            if (ev.key === 'Enter') {
                this._confirm();
            }
        };
    }
}

