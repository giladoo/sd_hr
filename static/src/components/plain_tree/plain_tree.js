/** @odoo-module */
import { registry } from "@web/core/registry"
import { Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useState, useRef, onMounted, onWillUnmount, onWillStart } from '@odoo/owl';

export class SdPlainTree extends Component {
    static template = "sd_hr.plain_tree_template";
    static props = {
        options: Object,
        onApi: Function,
    };
    setup(){
        this.state = useState({
            switcherElements: []
        })
        this.selectedNode;          // The selected node data
        this.selectedElement;       // The selected node element
        this.nodeData = {};         // Node data mapping { id: data }
        this.nodeElements = {};     // Node element mapping { id: element }
        this.options = {
                data: [],           // Tree-structured data [{ id, text, children }]
                contextMenu: [],    // Context menu config [{ text, onClick }]
                contextMenuArray: {},    // Context menu Array config { 'type': [{ text, onClick }]}
                contextMenuNames: [],    // Context menu Array config { 'type': [{ text, onClick }]}
                depth: 0,           // The default expansion depth of the tree
                onRendered: null,   // The callback event after the tree is rendered
                onNodeClick: null,   // The callback event when the node is clicked
                onSelectedNode: null,
            }

        this.containerRef = useRef("sd_plain_tree_element_ref")
//        this.options = Object.assign(this.options, this.props.options);
        onMounted(async () => {
            this.updateTree(this.props.options)

        });
        if (this.props.onApi) {
            this.props.onApi({
                expand: () => this.expand(),
                expandDepth: depth => this.expandDepth(depth),
                collapseDepth: depth => this.collapseDepth(depth),
                expandUp: node => this.expandUp(node),
                collapse: () => this.collapse(),
                updateNode: () => this.updateNode(),
                selectNode: (node_id, scroll) => this.selectNode(node_id, scroll=true),
                updateTree: options => this.updateTree(options),
            });
        }
        this.expand = this.expand.bind(this)

    }
    async updateTree(options){
//        console.log('up:',this.nodeElements)
        this.options = Object.assign(this.options, options);
        this.containerRef.el.innerHTML = ''
        this.createContextMenu();
        this.renderTree();
        if (this.selectedNode){
//            console.log('updateTree:', this.selectedNode)
            this.selectNode(this.selectedNode.id)
//            await this.collapse()
            await this.expandUp(this.selectedNode)
//            this.expand(this.selectedNode);

        }
    }
    async expandUp1(node){
    // todo: like expandDepth

    }
    async expandUp(node){
        if (typeof node == 'string'){
            node = this.nodeData[node]
        }
        const nodeEl = this.nodeElements[node.id];
        let parentElNode = nodeEl.parentNode
        if (parentElNode.classList.contains('plaintree-collapsed')) {
            const switcher = parentElNode.querySelector('.plaintree-switcher');
            switcher && switcher.click();
        } else if (parentElNode.classList.contains('plaintree-group')){
            parentElNode = nodeEl.parentNode.parentNode
            const switcher = parentElNode.querySelector('.plaintree-switcher');
            if (parentElNode.classList.contains('plaintree-collapsed')){
                switcher && switcher.click();
            }
        }

            const parentNode = this.nodeData[node.parent_id]
        if(!parentElNode.classList.contains('plaintree') && parentNode != undefined){
           this.expandUp(parentNode)
        }
    }
    expandDepth(depth){
        this.options.depth = depth
        const filteredNodes = Object.entries(this.nodeData).filter(node => node[1].depth < this.options.depth)
        filteredNodes.forEach(node => {
            const nodeEl = this.nodeElements[node[1].id];
            if (nodeEl.classList.contains('plaintree-collapsed')) {
                const switcher = nodeEl.querySelector('.plaintree-switcher');
                switcher && switcher.click();
            }
        })
    }
    collapseDepth(depth){
        this.options.depth = depth
        const filteredNodes = Object.entries(this.nodeData).filter(node => node[1].depth >= this.options.depth)
        filteredNodes.forEach(node => {
            const nodeEl = this.nodeElements[node[1].id];
            if (!nodeEl.classList.contains('plaintree-collapsed')) {
                const switcher = nodeEl.querySelector('.plaintree-switcher');
                switcher && switcher.click();
            }
        })
    }
    /** Expand the tree (expand the node when the parameter is specified, otherwise expand the root) */
    expand(node) {
        node = node || this.options.data;
        if (node instanceof Array) {
            node.forEach(n => this.expand(n));
            return;
        }
        // If the node is in a collapsed state, expand it
        const nodeEl = this.nodeElements[node.id];
        if (nodeEl.classList.contains('plaintree-collapsed')) {
            const switcher = nodeEl.querySelector('.plaintree-switcher');
            switcher && switcher.click();
        }
        // If there are child nodes, recursively expand them but do not exceed the specified depth
        node.children && node.children.forEach(child => {
            if (child.depth < this.options.depth) {
                this.expand(child);
            }
        });
    }

    /** Collapse the tree (collapse the node when the parameter is specified, otherwise collapse the root)*/
    collapse(node) {
        node = node || this.options.data;
        if (node instanceof Array) {
            node.forEach(n => this.collapse(n));
            return;
        }
        // If the node is in a expanded state, collapse it
        const nodeEl = this.nodeElements[node.id];
        if (!nodeEl.classList.contains('plaintree-collapsed')) {
            const switcher = nodeEl.querySelector('.plaintree-switcher');
            switcher && switcher.click();
        }
        // Recursive collapse the child nodes
        node.children && node.children.forEach(child => {
            this.collapse(child);
        });
    }

    /** Add a new node to the tree */
    addNode(node, parentId) {
        const parent = this.nodeData[parentId];
        if (!parent) throw new Error('Node parent not found: ' + parent);
        if (!parent.children) parent.children = [];
        parent.children.push(node);

        const parentEl = this.nodeElements[parentId];
        if (parent.children.length > 1) {
            // If a child node already exists, add the new node to the subtree container
            const groupEl = parentEl.querySelector('.plaintree-group');
            const nodeEl = this.createNodeElement(node);
            groupEl.append(nodeEl);
            // Cache new node data and elements
            node.depth = parent.depth + 1;
            this.nodeElements[node.id] = nodeEl;
            this.nodeData[node.id] = node;
            // Expand the parent node after added
            this.expand(parent);
        } else {
            // If there is no child node, create the subtree container first and then add it
            const subtreeEl = this.buildTree([node], parent.depth + 1);
            parentEl.append(subtreeEl);
            // Change the original leaf icon of the parent node to a switcher icon
            const icon = parentEl.firstChild;
            icon.classList.remove('plaintree-leaf');
            icon.classList.add('plaintree-switcher');
        }
    }

    /** Update a node in the tree */
    updateNode(node) {
        const nodeEl = this.nodeElements[node.id];
        if (!nodeEl) throw new Error('Node not found: ' + node);
        this.nodeData[node.id] = node; // Update node data
        nodeEl.querySelector('.plaintree-label').textContent = node.text;
    }

    /** Remove a node from the tree */
    removeNode(node) {
        const nodeEl = this.nodeElements[node.id];
        if (!nodeEl) throw new Error('Node not found: ' + node);

        const parentElNode = nodeEl.parentNode.parentNode;    // li.parentNode > ul.group > li.node
        const parentData = this.nodeData[parentElNode.nodeId];
        nodeEl.remove();

        // Remove from the children of the parent node
        parentData.children.splice(parentData.children.findIndex(n => n.id === node.id), 1);
        delete this.nodeData[node.id];     // Removed from the node data mapping
        delete this.nodeElements[node.id]; // Removed from the node element mapping

        // If the parent node has no children, change the icon to a leaf icon
        if (!parentData.children || !parentData.children.length) {
            parentElNode.firstChild.classList.remove('plaintree-switcher');
            parentElNode.firstChild.classList.add('plaintree-leaf');
        }
    }

    /** Render the tree structure */
    renderTree() {

        const rootEl = this.createRootElement();
        this.bindEvents(rootEl);
        rootEl.append(this.buildTree(this.options.data, 0));
        this.containerRef.el.append(rootEl);
//        // Callback after the tree is rendered
        if (this.options.onRendered) {
            this.options.onRendered.call(this, this, this.options.data);
        }

    }

    /** Build a tree based on the data */
    buildTree(data, depth) {
        const groupEl = this.createGroupElement();
        data.forEach(node => {
            // Cache node data and elements
            node.depth = depth;
            const nodeEl = this.createNodeElement(node, depth === this.options.depth);
            this.nodeElements[node.id] = nodeEl;
            this.nodeData[node.id] = node;

            // Recursive build subtrees
            if (node.children && node.children.length) {
                const subtreeEl = this.buildTree(node.children, depth + 1);
                nodeEl.append(subtreeEl);
            }
            groupEl.append(nodeEl);
        });
        return groupEl;
    }

    bindEvents(rootEl) {
        rootEl.addEventListener('click', e => {
            const { target } = e;
            if (target.nodeName === 'SPAN' &&
                target.classList.contains('plaintree-switcher')) {
                this.onSwitcherClick(target.parentNode);
            } else if (
                target.nodeName === 'SPAN' &&
                target.classList.contains('plaintree-label')) {
                this.onNodeClick(target.parentNode.nodeId);
            } else if (
                target.nodeName === 'LI' &&
                target.classList.contains('plaintree-node')) {
                this.onNodeClick(target.nodeId);
            }
        });
        // Giladoo
        const { contextMenuArray } = this.options;
        if (Object.keys(contextMenuArray) && Object.keys(contextMenuArray).length){
            Object.entries(contextMenuArray).forEach(contextMenu => {
                if (contextMenu[1] && contextMenu[1].length) {
                    if (this[`$${contextMenu[0]}`]) {
                        rootEl.addEventListener('contextmenu', e => {
                            e.preventDefault();
                            const { target } = e;
                            if (target.nodeName === 'SPAN' &&
                                target.classList.contains('plaintree-label') &&
                                target.parentNode.contextMenu === contextMenu[0]
                            ) {
                                this.selectNode(target.parentNode.nodeId, false);
                                this[`$${contextMenu[0]}`].style.left = `${e.pageX}px`;
                                this[`$${contextMenu[0]}`].style.top = `${e.pageY}px`;
                                this[`$${contextMenu[0]}`].style.display = 'block';
                            }else{
                                this[`$${contextMenu[0]}`].style.display = 'none';
                                if (this.$contextMenu){
                                     this.$contextMenu.style.display = 'none';                            }
                            }
                        });
                        // Click the blank area to hide the context menu
                        document.addEventListener('click', () => {
                            this[`$${contextMenu[0]}`].style.display = 'none';
                        });
                    }
                }
            })
        }
        if (this.$contextMenu) {
            rootEl.addEventListener('contextmenu', e => {
                e.preventDefault();
                const { target } = e;
                if (target.nodeName === 'SPAN' &&
                    target.classList.contains('plaintree-label') &&
                    !this.options.contextMenuNames.includes(target.parentNode.contextMenu)
                ) {

                    this.selectNode(target.parentNode.nodeId, false);
                    this.$contextMenu.style.left = `${e.pageX}px`;
                    this.$contextMenu.style.top = `${e.pageY}px`;
                    this.$contextMenu.style.display = 'block';
                }else{
                            this.$contextMenu.style.display = 'none';
                        }
            });
            // Click the blank area to hide the context menu
            document.addEventListener('click', () => {
                this.$contextMenu.style.display = 'none';
            });
        }

    }

    onNodeClick(id) {
        this.selectNode(id, false);
        if (this.options.onNodeClick) {
            this.options.onNodeClick.call(this, this.nodeData[id]);
        }
    }
// TODO: you need to keep expanded record to reopen then while rendering
    onSwitcherClick(nodeEl) {
        const el = nodeEl.lastChild;
        const height = el.scrollHeight;

        if (nodeEl.classList.contains('plaintree-collapsed')) {
//            this.state.switcherElements.push(nodeEl)
            this.animate(150, {
                enter() {
                    el.style.height = 0;
                    el.style.opacity = 0;
                },
                active() {
                    el.style.height = `${height}px`;
                    el.style.opacity = 1;
                },
                leave() {
                    el.style.height = '';
                    el.style.opacity = '';
                    nodeEl.classList.remove('plaintree-collapsed');
                }
            });
        } else {
//            this.state.switcherElements = this.state.switcherElements.filter( sel => sel !== nodeEl)

            this.animate(150, {
                enter() {
                    el.style.height = `${height}px`;
                    el.style.opacity = 1;
                },
                active() {
                    el.style.height = 0;
                    el.style.opacity = 0;
                },
                leave() {
                    el.style.height = '';
                    el.style.opacity = '';
                    nodeEl.classList.add('plaintree-collapsed');
                }
            });
        }
    }

    selectNode(id, scroll=true) {
        this.selectedNode = this.nodeData[id];
        this.options.selectedNode = this.nodeData[id];
        this.selectedElement && this.selectedElement.classList.remove('plaintree-selected');
        this.selectedElement = this.nodeElements[id];
        this.selectedElement.classList.add('plaintree-selected');
        scroll ?  setTimeout(() => this.selectedElement.scrollIntoView({ behavior: "smooth", block: "center", }) , 200)
         : false
    }

    // Giladoo
    createContextMenu() {
        const { contextMenu, contextMenuArray } = this.options;

        if (Object.keys(contextMenuArray) && Object.keys(contextMenuArray).length){
            Object.entries(contextMenuArray).forEach(contextMenu => {
                if (contextMenu[1] && contextMenu[1].length){
                    this.options.contextMenuNames.push(contextMenu[0]);

                    this[`$${contextMenu[0]}`] = document.createElement('div');
                    this[`$${contextMenu[0]}`].className = 'plaintree-context-menu';
                    this.containerRef.el.append(this[`$${contextMenu[0]}`]);

                    for (const item of contextMenu[1]) {
                        const option = document.createElement('div');
                        option.textContent = item.text;
                        option.addEventListener('click', () => item.onClick(this.selectedNode));
                        this[`$${contextMenu[0]}`].append(option);
                        }
                }
            })
        }
         if (contextMenu && contextMenu.length) {

            this.$contextMenu = document.createElement('div');
            this.$contextMenu.className = 'plaintree-context-menu';
            this.containerRef.el.append(this.$contextMenu);

            for (const item of contextMenu) {
                const option = document.createElement('div');
                option.textContent = item.text;
                option.addEventListener('click', () => item.onClick(this.selectedNode));
                this.$contextMenu.append(option);
            }
        }


    }

    createRootElement() {
        const div = document.createElement('div');
        div.classList.add('plaintree');
        return div;
    }

    createGroupElement = function() {
        const ul = document.createElement('ul');
        ul.classList.add('plaintree-group');
        return ul;
    }

    createNodeElement = function(node, collapsed) {
        const li = document.createElement('li');
        li.classList.add('plaintree-node');
        if (collapsed) {
            li.classList.add('plaintree-collapsed');
        }

        const isLeaf = !node.children || !node.children.length;
        const icon = document.createElement('span');
        icon.classList.add(isLeaf ? 'plaintree-leaf' : 'plaintree-switcher');
        li.append(icon);

        const label = document.createElement('span');
        label.classList.add('plaintree-label', );
        label.labelNodeId = node.id
        if (node.nodeClass){
            node.nodeClass.forEach(r => label.classList.add(r));
        }

        const text = document.createTextNode(node.text);
        label.append(text);
        li.append(label);
        li.nodeId = node.id;
        // Giladoo
        li.contextMenu = node.contextMenu;
        return li;
    }

    animate(duration, callback) {
        requestAnimationFrame(() => {
            callback.enter();
            requestAnimationFrame(() => {
                callback.active();
                setTimeout(() => callback.leave(), duration);
            });
        });
    }

}