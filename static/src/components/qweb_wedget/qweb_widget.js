/** @odoo-module **/

//import { registry } from '@web/core/registry';
//import { Field } from "@web/views/fields/field";
//import { qweb as QWeb } from '@web/core/qweb';

//class QWebWidget extends Field {
//    supportedFieldTypes = ['char', 'text'];

//    _render() {
//        this.el.innerHTML = '';
//        const context = { docs: JSON.parse(this.value) }; // Pass the data to the QWeb template
//        const html = QWeb.render('my_qweb_template', context);
//        this.el.innerHTML = html;
//    }
//}

//registry.category('fields').add('qweb_widget', QWebWidget);



import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart } from "@odoo/owl";

export class QWebWidgetComponent extends Component {
    setup() {
        this.actionService = useService("action");
        const user = useService('user');
        console.log('QWebWidgetComponent', this)
        onWillStart(async () => {
//            this.displayUOM = await user.hasGroup('uom.group_uom');
        });

    }

}

QWebWidgetComponent.template = 'sd_hr.my_qweb_template';
export const QWebWidget = {
    component: QWebWidgetComponent,
};
registry.category('fields').add('qweb_widget', QWebWidget);
