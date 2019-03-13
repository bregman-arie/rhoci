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
from rhoci.models.DFG import DFG

LOG = logging.getLogger(__name__)

from rhoci.DFG import bp  # noqa


@bp.route('/all')
def all_DFGs():
    """All DFGs."""
    DFGs_data = []
    DFGs = DFG.get_all_DFGs_based_on_jobs()
    for DFG_name in DFGs:
        DFGs_data.append({'name': DFG_name,
                          'num_of_jobs': Job.count(name_regex=DFG_name)})
    return render_template('DFG/all.html', DFGs=DFGs_data)


@bp.route('/squads')
def all_squads():
    """All squads."""
    squads_data = []
    DFGs = DFG.find()
    for DFG_db in DFGs:
        print(DFG_db)
        for squad in DFG_db['squads']:
            num_of_jobs = 0
            for component in squad['components']:
                num_of_jobs = num_of_jobs + Job.count(component)
            squads_data.append({'name': squad['name'],
                                'num_of_jobs': num_of_jobs})
    return render_template('DFG/all.html', DFGs=squads_data)


@bp.route('/components')
def all_components():
    """All components."""
    DFGs = DFG.find()
    for DFG_db in DFGs:
        print(DFG_db)


@bp.route('/<DFG_name>')
def summary():
    """All DFGs."""
    return render_template('')
