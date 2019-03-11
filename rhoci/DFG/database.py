# Copyright 2019 Arie Bregman
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
from __future__ import absolute_import

import re

from rhoci.database import Database


def get_all_DFGs():
    """Returns list of all DFGs based on jobs names.
    all_DFGs = [{'name': network, 'num_of_jobs': 20}, ...]
    """
    DFGs = []
    regex = re.compile('DFG-', re.IGNORECASE)
    DFG_jobs = Database.find(collection='jobs',
                             query={'name': regex})
    for job in DFG_jobs:
        jname = job['name']
        DFG_name = jname.split('-')[1] if '-' in jname else jname
        if DFG_name not in DFGs:
            DFGs.append(DFG_name)
    return DFGs
