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

from flask import current_app as app
from flask import render_template
from flask import url_for
import logging

from rhoci.models.job import Job
from rhoci.models.DFG import DFG

LOG = logging.getLogger(__name__)

from rhoci.DFG import bp  # noqa


@bp.route('/')
def DFGs():
    """All DFGs."""
    title = 'DFGs'
    DFGs_data = []
    all_DFGs = DFG.get_all_DFGs_based_on_jobs()
    for DFG_name in all_DFGs:
        uf = url_for('DFG.summary', DFG_name=DFG_name)
        DFGs_data.append({'name': DFG_name,
                          'num_of_jobs': Job.count(
                              name="DFG-{}".format(DFG_name)),
                          'summary_url_for': uf})
    return render_template('DFG/all.html', DFGs=DFGs_data, title=title)


@bp.route('/squads')
def squads():
    """All squads."""
    title = 'Squads'
    squads_data = []
    DFGs = DFG.find()
    for DFG_db in DFGs:
        if DFG_db['squads']:
            for squad in DFG_db['squads']:
                uf = url_for('DFG.squad_summary', DFG_name=DFG_db['name'],
                             squad_name=squad)
                num_of_jobs = 0
                for component in DFG_db['squad_to_components'][squad]:
                    num_of_jobs = num_of_jobs + Job.count(component)
                squads_data.append({'name': squad,
                                    'num_of_jobs': num_of_jobs,
                                    'summary_url_for': uf})
    return render_template('DFG/all.html', DFGs=squads_data, title=title)


@bp.route('/components')
def components():
    """All components."""
    title = 'Components'
    components_data = []
    DFGs = DFG.find()
    for DFG_db in DFGs:
        for component in DFG_db['components']:
            uf = url_for('DFG.component_summary', DFG_name=DFG_db['name'],
                         component_name=component)
            count = Job.count(component)
            components_data.append({'name': component,
                                    'num_of_jobs': count,
                                    'summary_url_for': uf})
    return render_template('DFG/all.html', DFGs=components_data, title=title)


@bp.route('/<DFG_name>')
def summary(DFG_name):
    """All DFGs."""
    uf = url_for('api.get_jobs', DFG_name=DFG_name)
    jenkins_url = app.config['custom']['jenkins']['url']
    pie = Job.get_builds_count_per_release(DFG=DFG_name)
    print(pie)
    return render_template('DFG/summary.html', DFG_name=DFG_name, uf=uf,
                           jenkins_url=jenkins_url, pie=pie)


@bp.route('/<DFG_name>/squad/<squad_name>')
def squad_summary(DFG_name, squad_name):
    """Specific squad summary."""
    uf = url_for('api.get_jobs', DFG_name=DFG_name, squad_name=squad_name)
    jenkins_url = app.config['custom']['jenkins']['url']
    return render_template('DFG/summary.html', DFG_name=DFG_name,
                           squad_name=squad_name, uf=uf,
                           jenkins_url=jenkins_url)


@bp.route('/<DFG_name>/component/<component_name>')
def component_summary(DFG_name, component_name):
    """Specific component summary."""
    uf = url_for('api.get_jobs', DFG_name=DFG_name,
                 component_name=component_name)
    jenkins_url = app.config['custom']['jenkins']['url']
    return render_template('DFG/summary.html', DFG_name=DFG_name,
                           component_name=component_name, uf=uf,
                           jenkins_url=jenkins_url)
