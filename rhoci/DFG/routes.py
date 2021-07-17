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
        failure_uf = url_for('DFG.builds_in_status', DFG_name=DFG_name, status='FAILURE')
        success_uf = url_for('DFG.builds_in_status', DFG_name=DFG_name, status='SUCCESS')
        unstable_uf = url_for('DFG.builds_in_status', DFG_name=DFG_name, status='UNSTABLE')
        DFGs_data.append({'name': DFG_name,
                          'summary_url_for': uf,
                          'failure_builds_uf': failure_uf,
                          'success_builds_uf': success_uf,
                          'unstable_builds_uf': unstable_uf,
                         })
    return render_template('DFG/all.html', DFGs=DFGs_data, title=title)


@bp.route('/<DFG_name>/summary')
def summary(DFG_name):
    """All DFGs."""
    squads_uf = {}
    uf = url_for('api.get_jobs', DFG_name=DFG_name)
    jenkins_url = app.config['custom']['jenkins']['url']
    pie = {}
    found_DFG = {'squads': []}
    return render_template('builds/index.html', DFG_name=DFG_name, uf=uf,
                           jenkins_url=jenkins_url, pie=pie,
                           squads=found_DFG['squads'], squads_uf=squads_uf)


@bp.route('/<DFG_name>/builds/<status>')
def builds_in_status(DFG_name, status):
    """Builds in specified status."""
    squads_uf = {}
    uf = url_for('api.get_jobs', DFG_name=DFG_name, status=status)
    jenkins_url = app.config['custom']['jenkins']['url']
    pie = {}
    found_DFG = {'squads': []}
    return render_template('builds/index.html', DFG_name=DFG_name, uf=uf,
                           jenkins_url=jenkins_url, pie=pie,
                           squads=found_DFG['squads'], squads_uf=squads_uf)
