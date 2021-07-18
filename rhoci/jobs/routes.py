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

from collections import Counter
from bson import json_util
from flask import current_app as app
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
import json
import logging

from rhoci.jenkins.jjb import generate_job_definition
from rhoci.models.job import Job
from rhoci.forms.dummy import Dummy
from rhoci.forms.job import JobSearch
from rhoci.forms.build import BuildSearch
from rhoci.forms.test import TestSearch

LOG = logging.getLogger(__name__)

from rhoci.jobs import bp  # noqa


@bp.route('/index')
@bp.route('/')
def index():
    uf = url_for('api.get_jobs')
    return render_template('builds/index.html', uf=uf)

@bp.route('/last_added')
def last_added():
    """Last added jobs."""
    jenkins_url = app.config['custom']['jenkins']['url']
    form = Dummy()
    query_str = {"last_added": 1}
    return render_template('jobs/last_added.html',
                           jenkins_url=jenkins_url,
                           query_str=query_str,
                           form=form)


@bp.route('/builds')
def builds():
    """All builds."""
    uf = url_for('api.all_builds')
    jenkins_url = app.config['custom']['jenkins']['url']
    return render_template('builds/index.html', uf=uf,
                           jenkins_url=jenkins_url)


@bp.route('/tests')
def tests():
    """All tests."""
    return render_template('tests/index.html')


@bp.route('/<name>')
def job(name):
    """Specific job summary."""
    uf = url_for('api.get_builds', job_name=name)
    job = Job.find(name=name)
    job[0].pop('_id')
    entity_json = json.dumps(job, indent=4, sort_keys=True,
                             default=json_util.default)
    jenkins_url = app.config['custom']['jenkins']['url']
    return render_template('jobs/one_job_summary.html', job_name=name,
                           uf=uf, jenkins_url=jenkins_url,
                           entity_json=entity_json)


@bp.route('/<name>/<number>')
def build(name, number):
    """Specific build summary."""
    uf = url_for('api.get_tests', job_name=name, build_number=number)
    entity = Job.find(name, build_number=int(number),
                      exact_match=True,
                      projection={"builds.$": 1, "_id": 0})
    entity_json = json.dumps(entity, indent=4, sort_keys=True,
                             default=json_util.default)
    jenkins_url = app.config['custom']['jenkins']['url']
    return render_template('builds/one_build_summary.html', job_name=name,
                           uf=uf, jenkins_url=jenkins_url, build_num=number,
                           entity_json=entity_json)


@bp.route('/exists')
def exists(DFG=None, tester=None, component=None):
    return False


@bp.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        output = generate_job_definition(jjb_data=request.form)
        return jsonify(output=output)
    else:
        form = Dummy()
        return render_template('jobs/generate.html', form=form)


@bp.route('/search', methods=['GET', 'POST'])
def search():
    uf = url_for('api.get_jobs')
    custom_search_uf = url_for('api.get_filtered_jobs')
    filters = [
        ('ip_version', str, ['ipv4', 'ipv6']),
        ('overcloud_ssl', str, ['yes', 'no']),
        ('storage_backend', str, ['ceph']),
        ('network_backend', str, ['geneve', 'vlan', 'vxlan']),
        ('l2gw', str, ['no', 'yes']),
        ('dvr', str, ['yes', 'no']),
        ('bgpvpn', str, ['yes', 'no']),
        ('osp_release', str, ['13', '14', '15', '16', '16.1', '16.2', '17'])
        ]
    return render_template('builds/search.html', uf=uf, search_pane=False, filters=filters,
                           custom_search_uf=custom_search_uf)


@bp.route('/tests/search', methods=['GET', 'POST'])
def search_tests():
    form = TestSearch()
    q = {}
    if request.method == 'POST':
        return redirect(url_for('tests.index', query=q))
    else:
        return render_template('tests/search.html', form=form)


@bp.route('/builds/search', methods=['GET', 'POST'])
def search_builds():
    form = BuildSearch()
    q = {}

    if request.method == 'POST':
        return redirect(url_for('builds.index', query=q))
    else:
        return render_template('builds/search.html', form=form)


@bp.route('/builds/active', methods=['GET', 'POST'])
def active_builds():
    pass
