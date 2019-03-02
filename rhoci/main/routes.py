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
from flask import render_template
import logging

LOG = logging.getLogger(__name__)

from rhoci.main import bp  # noqa


def get_DFG_summary(dfg):
    """Returns a dictionary which represents the summary of a given DFG."""
    pass


@bp.route('/')
def index():
    """Main page route."""
    DFGs_data = dict()
    DFGs = ['Network', 'Storage', 'Compute', 'Upgrades']
    for DFG in DFGs:
        DFGs_data[DFG] = get_DFG_summary(DFG)
    return render_template('main.html', DFGs_to_display=DFGs, DFGs=DFGs_data)
