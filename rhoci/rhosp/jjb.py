# Copyright 2017 Arie Bregman
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import os

TESTER_TO_TEMPLATE = {
    'pep8': 'single_node_jobs.j2',
    'unit': 'single_node_jobs.j2',
    'fullstack': 'single_node_jobs.j2',
    'functional': 'single_node_jobs.j2',
    'fullstack': 'single_node_jobs.j2',
    'tempest': 'tempest_normal_jobs.j2',
}

DEFAULT_TEMPLATE = 'single_node_jobs.j2'
TEMPLATES_DIR = os.path.dirname(__file__) + '/templates'


def get_template(tester):
    """Returns template path based on a given tester."""
    template = TESTER_TO_TEMPLATE.get(tester.lower(), DEFAULT_TEMPLATE)

    with open(TEMPLATES_DIR + '/' + template, 'r+') as f:
        template_content = f.read()

    return template_content
