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
from flask import jsonify
from flask import render_template
from flask import request
from flask import url_for
import logging

from rhoci.jenkins.jjb import generate_job_definition
from rhoci.forms.dummy import Dummy

LOG = logging.getLogger(__name__)

from rhoci.jobs import bp  # noqa


@bp.route('/index')
@bp.route('/')
def index():
    """All jobs."""
    jenkins_url = app.config['custom']['jenkins']['url']
    query_str = request.args.to_dict()
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
    jenkins_url = app.config['custom']['jenkins']['url']
    return render_template('jobs/one_job_summary.html', job_name=name,
                           uf=uf, jenkins_url=jenkins_url)


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
    if request.method == 'POST':
        pass
    else:
        form = Dummy()
        return render_template('jobs/search.html', form=form)
