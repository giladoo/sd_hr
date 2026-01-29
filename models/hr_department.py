# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, tools
from collections import defaultdict
import json
from icecream import ic

class SdHrDepartments(models.Model):
    _inherit = "hr.department"

    def _build_plain_tree(self, data, dep_list, job_list=[], emp_list=[]):

        # Step 1: Build reverse mapping (parent → list of children)
        children_map = defaultdict(list)
        for child_id, parent_id in data.items():
            if parent_id is not False:
                children_map[parent_id].append(child_id)
        def add_parent(record, node_id):
            child = record.get(node_id)
            # child['parent_id'] = record['id']
            return child

        # Step 2: Recursive function to build tree nodes
        def build_node(node_id):
            node = dep_list[node_id]
            children = children_map.get(node_id, [])
            # add jobs as department children
            node['children'] = [add_parent(r, node_id) for r in job_list if r.get(node_id, False)] if job_list else []
            # add employees without job position as department children
            node_child = [r.get(node_id) for r in emp_list if r.get(node_id)] if emp_list else []
            node['children'] += node_child[0] if node_child else []
            if children:
                node['children'] += [build_node(child_id) for child_id in children]
            return node
        # Step 3: Build tree from root nodes
        tree = []
        for node_id, parent_id in data.items():
            if parent_id is False:
                tree.append(build_node(node_id))

        return tree

    def get_departments(self):
        is_fa = True if self.env.context.get('lang', '') == 'fa_IR' else False

        # 1 create employees data as employees
        employees = self.env['hr.employee'].search([],order='sequence')

        # 2 create jobs data as jobs
        jobs = self.env['hr.job'].search([],order='sequence')
        # 3 create departments data as departments
        departments = self.search([],order='name')

        job_list = []
        for job in jobs:
            # 4 link employees as job child jobs_list
            emp_jobs = employees.filtered(lambda rec: rec.job_id.id == job.id)
            job_children = [{
                'text': emp.name,
                'parent_id': f"job_{emp.job_id.id}",
                'model': 'hr.employee',
                'contextMenu': 'contextMenuEmployee',
                'id': f"emp_{emp.id}",
            } for emp in emp_jobs]

            # 5 link jobs_list to departments
            department_id = job.department_id.id if job.department_id else 'False'
            job_list.append({
                department_id: {
                        'text': job.name,
                        'department_id': department_id,
                        'parent_id': f"dep_{department_id}",
                        'model': 'hr.job',
                        'id': f"job_{job.id}",
                        'children': job_children,
                        'nodeClass': ['text-primary', 'bg-warning-light', 'px-3', 'rounded', ],
                        'contextMenu': 'contextMenuJob',
                        }
                })
        # 6 create departments parent dict
        dep_parents = dict({rec.id: rec.parent_id.id for rec in departments})
        dep_parents['False'] = False

        # 7 create departments data list
        dep_list = dict({rec.id: {
                        'text': f"\u200F{rec.name} ({rec.manager_id.name or ''})" if is_fa else f"{rec.name} ({rec.manager_id.name or ''})",
                        'id': f"dep_{rec.id}",
                        'parent_id': f"dep_{rec.parent_id.id}" if rec.parent_id else False,
                        'model': 'hr.department',
                        'contextMenu': 'contextMenuDepartment',
                        'nodeClass': ['text-primary', 'px-3', 'rounded',  'bg-400' ],                                    }
                                   for rec in departments
                                   })
        dep_list['False'] = {'text': _('Department is not set'), 'id':'False'}
        # ic(dep_list)

        # 8 create list of employees without job position as emp_no_jobs
        emp_no_job = employees.filtered(lambda rec: not rec.job_id).grouped('department_id')
        dep_children = []
        emp_no_job_list = []
        # 9 link emp_no_jobs to departments
        for dep, emps in emp_no_job.items():
            # print(f"{dep.id}: {len(emps)}")
            dep_children = [{
                'text': emp.name,
                'model': 'hr.employee',
                'contextMenu': 'contextMenuEmployee',
                'parent_id': f"dep_{emp.department_id.id}" if emp.department_id else False,
                'id': f"emp_{emp.id}",

            } for emp in emps]
            emp_no_job_list.append({dep.id or 'False': dep_children})

        # 10 build plain tree data
        plain_tree = self._build_plain_tree(dep_parents, dep_list, job_list, emp_no_job_list)
        # ic(plain_tree)
        return json.dumps(plain_tree)


