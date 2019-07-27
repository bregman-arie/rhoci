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

LOG = logging.getLogger(__name__)

from rhoci.jobs import bp  # noqa


@bp.route('/index')
@bp.route('/')
def index():
    """All jobs."""
    jenkins_url = app.config['custom']['jenkins']['url']
    query_str = request.args.to_dict()
    if 'query' in query_str:
        query_str = query_str['query']
    print(query_str)
    form = Dummy()
    return render_template('jobs/index.html',
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
    job_json = json.dumps(job, indent=4, sort_keys=True,
                          default=json_util.default)
    jenkins_url = app.config['custom']['jenkins']['url']
    return render_template('jobs/one_job_summary.html', job_name=name,
                           uf=uf, jenkins_url=jenkins_url, job_json=job_json)


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
        print(request.args)
        return redirect(url_for('jobs.index', query=q))
    else:
        return render_template('jobs/search.html', form=form)
