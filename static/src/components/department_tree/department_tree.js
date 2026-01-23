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
        this._openNode = this._openNode.bind(this)
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
    _openNode(node, viewType="form", domain=[], context={}){
        console.log('node:', node)
        let actionData = {
                type: "ir.actions.act_window",
                name: "",
                res_model: node.model,
                view_mode: viewType,
                views: [[false, viewType],],
                target: "new",
                res_id: node.id,
                domain: domain,
                context: context,
            }
        if (["hr.department", "hr.job", "hr.employee"].includes(node.model) && viewType == 'form'){

        }
        else if (node.model == 'hr.contract'){
            actionData = {
                type: "ir.actions.act_window",
                name: "",
                res_model: 'hr.contract',
                view_mode: viewType,
                views: [[false, viewType],],
                target: "new",
                domain: domain,
                context: context,
            }
        } else{
            return
        }
        this.actionService.doAction(
                     actionData,
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
        let newNode = {}
        this.tree = new PlainTree('#tree_element', {
            data,
            depth: 2,
            onRendered: null ,
               contextMenu: [
                            {
                             text: _t('New Department'),
                             onClick: (node) => {
                                newNode = {...node}
                                newNode.id = 0
                                this._openNode(newNode, 'form', [], {'default_parent_id': node.id})
                             }
                           },
                            {
                             text: _t('New Employee'),
                             onClick: (node) => {
                                console.log('New Employee', node)
                                newNode = {...node}
                                if (node.model == 'hr.department'){
                                    newNode.id = 0
                                    newNode.model = "hr.employee"
                                    this._openNode(newNode, 'form', [], {'default_department_id': node.id})
                                    }
                                   else if (node.model == 'hr.job'){
                                    newNode.id = 0
                                    newNode.model = "hr.employee"
                                    this._openNode(newNode, 'form', [], {'default_job_id': node.id, 'default_department_id': node.department_id})
                                  }
                                  }
                           },
                            {
                             text: _t('New Job Position'),
                             onClick: (node) => {
                                console.log('node', node)
                             }
                           },
                            {
                             text: _t('Contract List'),
                             onClick: (node) => {
                                console.log('node', node)
                                if (node.model == 'hr.employee'){
                                    newNode = {...node}
                                    newNode.model = 'hr.contract'
                                    this._openNode(newNode, 'list', [['employee_id', '=', newNode.id]])
                                }
                             }
                           },
                           ],
            onNodeClick: (node) => {
                console.log('onNodeClick:', node)
                this._openNode(node)
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
