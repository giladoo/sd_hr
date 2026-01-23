# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, tools
from collections import defaultdict
import json
from icecream import ic

class SdHrDepartments(models.Model):
    _inherit = "hr.department"

    def _build_plain_tree(self, data, departments):
        is_fa = True if self.env.context.get('lang', '') == 'fa_IR' else False

        # Step 1: Build reverse mapping (parent → list of children)
        children_map = defaultdict(list)
        for child_id, parent_id in data.items():
            if parent_id is not False:
                children_map[parent_id].append(child_id)

        # Step 2: Recursive function to build tree nodes
        def build_node(node_id):
            doc = departments[node_id]
            node = {
                'text': f"\u200E{doc['code']} - \u200F{doc['name']}" if is_fa else f"{doc['code']} - {doc['name']}",
                'id': node_id,
                'type': doc['type'],
            }
            children = children_map.get(node_id, [])
            if children:
                node['children'] = [build_node(child_id) for child_id in children]
            return node

        # Step 3: Build tree from root nodes
        tree = []
        for node_id, parent_id in data.items():
            if parent_id is False:
                tree.append(build_node(node_id))

        return tree

    def _build_hierarchy(self, data):

        # Step 1: Build reverse mapping (parent → list of children)
        children_map = defaultdict(list)
        for child, parent in data.items():
            if parent is not False:
                children_map[parent].append(child)

        # Step 2: Recursive function to build nested dict
        def build_tree(node):
            return {child: build_tree(child) for child in children_map.get(node, [])}

        # Step 3: Build final structure from root nodes
        result = {}
        for node, parent in data.items():
            if parent is False:
                result[node] = build_tree(node)

        return result

    def find_child(self, records, record):
        return tuple((rec.id for rec in records if rec.parent_id == record))

    def find_parent(self, records, record):
        return tuple((rec.id for rec in records if rec.parent_id == record))

    def get_departments(self):
        is_fa = True if self.env.context.get('lang', '') == 'fa_IR' else False
        def parent(rec):
            if rec['parent_id']:
                rec['parent_id'] = rec['parent_id'][0]
            return rec

        departments = self.search_read([], ['id', 'name', 'parent_id', 'child_ids', 'manager_id', ],order='name')
        departments = list([parent(rec) for rec in departments])
        top_chart_ids = list([rec['id'] for rec in departments if not rec['parent_id']])
        jobs = self.env['hr.job'].search_read([], ['name', 'department_id'])
        jobs_grouped = dict(tools.groupby(jobs, key=lambda a: a['department_id']))

        employees = self.env['hr.employee'].search_read([], ['name', 'department_id', 'job_id'])

        employee_dep_grouped = dict(tools.groupby(employees, key=lambda a: a['department_id']))
        employee_job_grouped = dict(tools.groupby(employees, key=lambda a: a['job_id']))
        char_list = list([{
                            'id': rec['id'],
                            'text': f"\u200F{rec['name']} (\u200F{rec['manager_id'][1] if rec['manager_id'] else ''})" if is_fa
                            else f"{rec['name']} ({rec['manager_id'][1] if rec['manager_id'] else ''})",
                            'children': rec['child_ids'],
                            'model': 'hr.department',
                             'nodeClass': ['text-primary', 'border', 'border-primary', 'px-3', 'rounded', ],
                           } for rec in departments
                          ])
        print(f".............len(char_list): {len(char_list)}")


        # ic(employee_job_grouped)



        new_deps = list()
        char_list_1 = list([rec for rec in char_list])
        job_employees_ids = []
        for i in range(len(char_list) + 1):
            deps = list([rec for rec in char_list_1 if rec['children'] and len(rec['children']) == i and isinstance(rec['children'][0], int)])
            # print(f">>>>>>>> i: {i} len(deps):{len(deps)}\n {deps}\n\n")
            for d in deps:
                new_d = dict({k:v for k,v in d.items()})
                # new_d =
                new_ch = list()
                for c_id in d['children']:
                    nc = list([rc for rc in char_list if rc['id'] == c_id and rc['model'] == 'hr.department'])
                    if nc:
                        dep_jobs = list([v for k, v in jobs_grouped.items() if k and k[0] == nc[0]['id']])
                        if dep_jobs:
                            for dep_job in dep_jobs[0]:
                                job_employee_list = []
                                # TODO: some employees cannot be excepted from department while are in job list
                                job_employees = list([v for k, v in employee_job_grouped.items() if k and k[0] == dep_job['id']])
                                job_employees_ids += list([e['id'] for e in job_employees[0]]) if job_employees else []
                                ic(job_employees)
                                ic(job_employees_ids)
                                if job_employees:
                                    for job_employee in job_employees[0]:
                                        job_employee_data = {
                                            'id': job_employee['id'],
                                            'text': job_employee['name'],
                                            'children': [],
                                            'model': 'hr.employee',
                                        }
                                        job_employee_list.append(job_employee_data)
                                dep_job_data = {
                                    'id': dep_job['id'],
                                    'text': dep_job['name'],
                                    'children': job_employee_list,
                                    'nodeClass': ['text-primary', 'border', 'border-warning', 'px-3', 'rounded', ],
                                    'model': 'hr.job',
                                }
                                nc[0]['children'].append( dep_job_data)
                        dep_employees = list(
                            [v for k, v in employee_dep_grouped.items()
                             if k and k[0] == nc[0]['id'] and v[0]['id'] not in job_employees_ids])
                        ic(dep_employees)

                        if dep_employees:
                            for dep_employee in dep_employees[0]:
                                dep_employee_data = {
                                    'id': dep_employee['id'],
                                    'text': dep_employee['name'],
                                    'children': [],
                                    'model': 'hr.employee',
                                }
                                nc[0]['children'].append( dep_employee_data)

                        new_ch.append(nc[0])

                        # new_ch.append( dict({'id': 41, 'text': 'ICT MANAGER', 'model': 'hr.jop'}))
                    else:
                        new_ch.append([])
                for r in char_list_1:
                    if r['id'] == d['id']:
                        r['children'] = new_ch


                # ic('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                # ic(new_ch)
                new_d['children'] = new_ch
                new_deps.append(new_d)
        new_top_chart = list([rec for rec in new_deps if rec['id'] in top_chart_ids])
        # ic(top_chart_ids)
        # ic(new_deps)

        # data_pc = [{'text': 'Arash',
        #          'id': 200,
        #          'children':[
        #              {'text': 'Atousa', 'id': 201},
        #              {'text': 'Barbod', 'id': 202},
        #              {'text': 'Yasamin', 'id': 203, 'children':[{'text': 'Yasamin 1', 'id': 211},]}
        #          ]
        #          }]
        return json.dumps(new_top_chart)
