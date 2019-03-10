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

from flask import render_template
import logging

from rhoci.models.job import Job

LOG = logging.getLogger(__name__)

from rhoci.DFG import bp  # noqa


@bp.route('/all')
def all():
    """All DFGs."""
    DFGs_data = []
    DFGs = Job.get_all_DFGs()
    for DFG in DFGs:
        DFGs_data.append({'name': DFG,
                          'num_of_jobs': Job.count(name_regex=DFG)})
    return render_template('DFG/all.html', DFGs=DFGs_data)


@bp.route('/<DFG_name>')
def summary():
    """All DFGs."""
    return render_template('')
