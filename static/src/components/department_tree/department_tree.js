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
            search: [],
            labelTags: [],
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
        this.onFindNext = this.onFindNext.bind(this)
        this.loadPlainTree = this.loadPlainTree.bind(this)
    }
    async _getData(){
        let getDepartments = await this.orm.call('hr.department', 'get_departments', [false])
        getDepartments = JSON.parse(getDepartments)
        return getDepartments

    }
    nodeId(node){
        return node.id ? Number(node.id.split('_')[1]) : 0
    }
    _openNode(node, viewType="form", domain=[], context={}){
        node.id = this.nodeId(node)
        console.log("_openNode", context)
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
        if (viewType == "list,form"){
            actionData.view_mode = 'list,form'
            let views = viewType.split(',')
            console.log('viewType', views)
            actionData.views = []
            views.forEach(r => actionData.views.push([false, r]))
            actionData.views =  [[false, 'list'],]
//            actionData.action_xml_id =  "sd_hr."
            actionData.xml_id =  "sd_hr.employee_add_to_list_action"
            console.log('viewType', actionData.views)
        }
        if (["hr.department", "hr.job", "hr.employee"].includes(node.model)){

        } else if (node.model == 'hr.contract'){
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
                            this.onRefresh();
                        },
                    })
    }

    async onRefresh(e){
        let data = await this._getData()
        this.tree_element.el.innerHTML = ''
        this.loadPlainTree(data)

    }
    loadPlainTree(data){
        console.log('data:', data)
        let newNode = {}
        this.tree = new PlainTree('#tree_element', {
            data,
            depth: 10,
            onRendered: null ,
            contextMenu: [
                            {
                             text: _t('Expand'),
                             onClick: (node) => {
                                this.tree.expand([node])
                             }
                           },
                            {
                             text: _t('New Department'),
                             onClick: (node) => {
                                if(node.model == 'hr.department'){
                                    newNode = {...node}
                                    newNode.id = 0
                                    this._openNode(newNode, 'form', [], {'default_parent_id': this.nodeId(node)})
                                }
                             }
                           },
                            {
                             text: _t('Employees'),
                             onClick: (node) => {
                                newNode = {...node}
                                newNode.id = 0
                                newNode.model = "hr.employee"
                                this._openNode(newNode, 'list,form', [],
                                 {create: false,
                                 default_department_id: node.department_id,
                                 node_model: node.model,
                                 node_id: node.id,
                                 })
                             }
                           },
                            {
                             text: _t('New Employee'),
                             onClick: (node) => {
                                console.log('New Employee', node)
                                newNode = {...node}
                                if (node.model == 'hr.job'){
                                    newNode.id = 0
                                    newNode.model = "hr.employee"
                                    this._openNode(newNode, 'form', [], { 'default_department_id': node.department_id, 'default_job_id': this.nodeId(node),})
                                  }
                                  }
                           },
                            {
                             text: _t('New Job Position'),
                             onClick: (node) => {
                                newNode = {...node}
                                newNode.id = 0
                                newNode.model = "hr.job"
                                this._openNode(newNode, 'form', [], {'default_department_id': this.nodeId(node)})
                             }

                           },
                            {
                             text: _t('Contract List'),
                             onClick: (node) => {
                                if (node.model == 'hr.employee'){
                                    newNode = {...node}
                                    newNode.model = 'hr.contract'
                                    this._openNode(newNode, 'list', [['employee_id', '=', Number(newNode.id.split('_')[1])]])
                                }
                             }
                           },                            {
                             text: _t('Jobs List'),
                             onClick: (node) => {
                                if (node.model == 'hr.department'){
                                    newNode = {...node}
                                    newNode.model = 'hr.job'
                                    this._openNode(newNode, 'list', [['department_id', '=', Number(newNode.id.split('_')[1])]])
                                }
                             }
                           },                            {
                             text: _t('Employee List'),
                             onClick: (node) => {
                                if (node.model == 'hr.job'){
                                    newNode = {...node}
                                    newNode.model = 'hr.employee'
                                    this._openNode(newNode, 'list', [['job_id', '=', Number(newNode.id.split('_')[1])]])
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
        this.tree.expand()
    }
    onCollapse(){
        this.tree.collapse()
    }
    _onSearch(e){
        let searchValue = e.target.value
        const allLabels = document.querySelectorAll('span.plaintree-label')
        if( e.keyCode == 13){
            this.state.search = ['']
            e.target.value = ''
        } else{
            this.state.search = searchValue.toLowerCase()
            allLabels.forEach(l => l.classList.contains('text-danger') ? l.classList.remove('text-danger') : false)
            this.state.labelTags = []
            allLabels.forEach(l => {
                if (searchValue && l.innerText.includes(searchValue)){
                    this.state.labelTags.push(l)
                    l.classList.add('text-danger')
                }
            })
        }
    }
    onFindNext(e){
        const firstLabel = this.state.labelTags.shift()
        firstLabel.scrollIntoView({ behavior: "smooth", block: "center", inline: "nearest" })
        this.state.labelTags.push(firstLabel)

    }
}

registry.category("actions").add("sd_hr.department_tree", SdHrDepartmentTree);
