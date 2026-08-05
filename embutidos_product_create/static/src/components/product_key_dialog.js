import { Dialog } from '@web/core/dialog/dialog';
import { Component, useState } from '@odoo/owl';

export class ProductKeyDialog extends Component {
    static template = 'embutidos.ProductKeyDialog';
    static components = { Dialog };
    static props = ['title', 'placeholder', 'startingValue', 'close', 'getPayload'];

    setup() {
        this.state = useState({ value: this.props.startingValue || '' });
    }

    confirm() {
        // resolve with the entered value
        this.props.getPayload(this.state.value);
        this.props.close();
    }

    cancel() {
        // resolve with undefined to indicate cancel
        this.props.getPayload();
        this.props.close();
    }
}

