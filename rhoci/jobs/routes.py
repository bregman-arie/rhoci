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

PROJECTION = {'name': 1, 'last_build': 1, 'release': 1, 'last_successful_build': 1,
              'tester': 1}
LOG = logging.getLogger(__name__)

from rhoci.jobs import bp  # noqa


@bp.route('/index')
@bp.route('/')
def index():
    """All jobs."""
    jenkins_url = app.config['custom']['jenkins']['url']
    query_str = request.args.to_dict()
    query_s = request.args.to_dict()
    if 'query' in query_str:
        query_str = eval(query_str['query'])
        jobs = Job.find(query_str=query_str, projection=PROJECTION)
    else:
        jobs = Job.find(projection=PROJECTION)
    form = Dummy()
    statuses = Counter([job['last_build']['status'] for job in jobs if 'status' in job['last_build']])
    releases = Counter([job['release'] for job in jobs if 'release' in job and job['release']])
    testers = Counter([job['tester'] for job in jobs if 'tester' in job and job['tester']])
    if "query" in query_s:
        query_string = query_s['query']
    else:
        query_string = query_s
    return render_template('jobs/index.html',
                           jenkins_url=jenkins_url,
                           query_str=query_string,
                           releases=dict(releases),
                           statuses=dict(statuses),
                           testers=dict(testers),
                           form=form)


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
    form = JobSearch()
    q = {}
    if form.name.data:
        q['name'] = form.name.data
    if form.release.data:
        q['release'] = form.release.data
    if form.DFG.data:
        q['DFG'] = form.DFG.data
    if form.squad.data:
        q['squad'] = form.squad.data
    if form.component.data:
        q['component'] = form.component.data
    if form.tester.data:
        q['tester'] = form.tester.data
    if form.job_class.data:
        q['class'] = form.job_class.data

    if request.method == 'POST':
        return redirect(url_for('jobs.index', query=q))
    else:
        return render_template('jobs/search.html', form=form)


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
