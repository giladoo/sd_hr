/** @odoo-module */

import { registry } from '@web/core/registry';
import { FormController } from '@web/views/form/form_controller';

class ExampleFormController extends FormController {
    setup() {
        console.log('ExampleFormController')
        super.setup();
        this.attachmentsButtonClick = this.attachmentsButtonClick.bind(this);
        this.el.querySelector('.o_attach_button').addEventListener('click', this.attachmentsButtonClick);
    }

    async attachmentsButtonClick() {
        const { res_id, res_model } = this.model.root.data;
        this.trigger_up('attachment_view', {
            action: 'attachment',
            name: "Attachments",
            target: 'current',
            context: {
                default_res_id: res_id,
                default_res_model: res_model,
            }
        });
    }
}

registry.category('views').add('example_form_controller', ExampleFormController);
