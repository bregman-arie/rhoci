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
import re

import rhoci.rhosp.DFG as DFG_lib


def get_job_type(name):
    """Returns job type based on its name."""
    if 'phase1' in name:
        return 'phase1'
    elif 'phase2' in name:
        return 'phase2'
    elif 'dfg' in name:
        dfg = DFG_lib.get_DFG_name(name)
        if not DFG_lib.dfg_exists(dfg):
            DFG_lib.add_dfg_to_db(dfg)
        return 'dfg'
    else:
        return 'other'


def get_job_release(name):
    """Returns release number as string."""
    m = re.search('-\d{1,2}', name)
    return m.group().split('-')[1] if m else 0
