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
from flask import url_for
import logging

from rhoci.models.job import Job
from rhoci.models.DFG import DFG

LOG = logging.getLogger(__name__)

from rhoci.DFG import bp  # noqa


@bp.route('/all')
def all_DFGs():
    """All DFGs."""
    title = 'DFGs'
    DFGs_data = []
    DFGs = DFG.get_all_DFGs_based_on_jobs()
    for DFG_name in DFGs:
        uf = url_for('DFG.summary', DFG_name=DFG_name)
        DFGs_data.append({'name': DFG_name,
                          'num_of_jobs': Job.count(name_regex=DFG_name),
                          'summary_url_for': uf})
    return render_template('DFG/all.html', DFGs=DFGs_data, title=title)


@bp.route('/squads')
def all_squads():
    """All squads."""
    title = 'Squads'
    squads_data = []
    DFGs = DFG.find()
    for DFG_db in DFGs:
        if DFG_db['squads']:
            for squad in DFG_db['squads']:
                uf = url_for('DFG.squad_summary', DFG_name=DFG_db['name'],
                             squad_name=squad['name'])
                num_of_jobs = 0
                for component in squad['components']:
                    num_of_jobs = num_of_jobs + Job.count(component)
                squads_data.append({'name': squad['name'],
                                    'num_of_jobs': num_of_jobs,
                                    'summary_url_for': uf})
    return render_template('DFG/all.html', DFGs=squads_data, title=title)


@bp.route('/components')
def all_components():
    """All components."""
    title = 'Components'
    components_data = dict()
    DFGs = DFG.find()
    for DFG_db in DFGs:
        print(DFG_db)
    return render_template('DFG/all.html', DFGs=components_data, title=title)


@bp.route('/<DFG_name>')
def summary(DFG_name):
    """All DFGs."""
    return render_template('DFG/summary.html', DFG_name=DFG_name)


@bp.route('/<DFG_name>/squad/<squad_name>')
def squad_summary(DFG_name, squad_name):
    """All DFGs."""
    return render_template('DFG/squad/summary.html', DFG_name=DFG_name,
                           squad_name=squad_name)
