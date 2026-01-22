/** @odoo-module */
import { registry } from "@web/core/registry"
import { Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useState, useRef, onMounted, onWillUnmount, onWillStart } from '@odoo/owl';
import { download } from "@web/core/network/download";
import { browser } from "@web/core/browser/browser";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
const { DateTime } = luxon;
import { formatDate } from "@web/core/l10n/dates";
import { usePopover } from "@web/core/popover/popover_hook";
import { Tooltip } from "@web/core/tooltip/tooltip";
import { loadBundle } from "@web/core/assets";
import { loadJS } from "@web/core/assets";

export class SdHrDepartmentTree extends Component {
    static template = "sd_hr.department_tree_template"
    setup(){

        let self = this;
        this.orm = useService('orm')
        this.actionService = useService("action")
        this.tree_element = useRef('tree_element')

        this.state = useState({
            departments: [],
        })
        onWillStart(async () => {
            const plainTree = '/sd_hr/static/src/lib/plain_tree/plain_tree.js'
            await loadJS(plainTree)
        });
        onMounted(async () => {
            let oActionManager = document.querySelector('.o_action_manager')
            oActionManager && (oActionManager.style.overflowY = 'auto')
            let data = await this._getData()
            this.loadPlainTree(data)
        });
        onWillUnmount(()=>{
            let oActionManager = document.querySelector('.o_action_manager')
            oActionManager && (oActionManager.style.overflowY = '')
        })
        this._openDepartment = this._openDepartment.bind(this)
        this.onRefresh = this.onRefresh.bind(this)
        this.onExpand = this.onExpand.bind(this)
        this.onCollapse = this.onCollapse.bind(this)
        this.loadPlainTree = this.loadPlainTree.bind(this)
        this._onFormClose = this._onFormClose.bind(this)
    }
    async _getData(){
        let getDepartments = await this.orm.call('hr.department', 'get_departments', [false])
        getDepartments = JSON.parse(getDepartments)
        return getDepartments

    }
    _openDepartment(node){
        console.log('node:', node)
        let name = "";
        let domain = [];
        let context = {};
        let res_model = node.model;
        let view_mode = "form";
        let views = [[false, "form"],];
        let target = "new"
        let res_id = node.id
        if (["hr.department", "hr.job", "hr.employee"].includes(node.model)){

        }
        else if (node.model == ''){

        } else{
            return
        }
        this.actionService.doAction(
            {
                type: "ir.actions.act_window",
                name: name,
                res_model: res_model,
                views: views,
                view_mode: view_mode,
                target: target,
                res_id: node.id,
                domain: domain,
                context: context,

            },
                    {
                        onClose: (e) => {
                            // Comment: if refresh, you lost the last track of work. if not you need to refresh manually
//                            this.onRefresh();
                        },
                    })

    }
    _onFormClose(res_id){
//        console.log('_onFormClose', res_id, this)
//        this.tree.onExpand();
    }
    async onRefresh(e){
        let data = await this._getData()
        this.tree_element.el.innerHTML = ''
        this.loadPlainTree(data)

    }
    loadPlainTree(data){
        this.tree = new PlainTree('#tree_element', {
            data,
            depth: 2,
            onRendered: null ,
            onNodeClick: (node) => {
//                console.log('id:', id)
                this._openDepartment(node)
            },
        });
//        this.tree.collapse()
    }
    onExpand(){
        console.log('tree', this.tree)
//        this.tree['#options']['depth'] = 3
        this.tree.expand()
    }
    onCollapse(){
        this.tree.collapse()
    }
}

registry.category("actions").add("sd_hr.department_tree", SdHrDepartmentTree);
