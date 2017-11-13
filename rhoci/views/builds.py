# Copyright 2017 Arie Bregman
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
from flask import Blueprint
import jenkins
from flask import jsonify
from flask import request
import logging

from rhoci.models import Agent
from rhoci.models import Build
from rhoci.models import Job


logger = logging.getLogger(__name__)

builds = Blueprint('builds', __name__)


@builds.route('/tests_compare')
def tests_compare():
    """Comparing tests of two different builds."""

    return render_template('tests_compare.html')


@builds.route('/job_exists/', methods=['GET'])
@builds.route('/job_exists/<job_name>', methods=['GET'])
def job_exists(job_name=None):

    return jsonify(exists=job_exists)


@builds.route('/active_builds', methods=['GET'])
def active():

    db_builds = Build.query.filter_by(active=True)
    builds = [build.serialize for build in db_builds]
    agent = Agent.query.one()

    return render_template('active_builds.html', agent=agent, builds=builds)


@builds.route('/builds', methods=['GET'])
def all_builds():

    db_builds = Build.query.all()
    all_builds = [build.serialize for build in db_builds]

    return render_template('builds.html', all_builds=all_builds)


@builds.route('/failure_anaylze', methods=['GET'])
def failure_analyze():

    return render_template('failure_analyzer.html')


@builds.route('/exists/')
def exists():
    job = request.args.get('job')
    build = int(request.args.get('build'))
    exists = True
    message = ''

    if not job or not build:
        exists = False
        message = "Invalid input"
    elif not Job.query.filter_by(name=job).count():
        agent = Agent.query.one()
        conn = jenkins.Jenkins(agent.url, agent.user, agent.password)
        exists = conn.job_exists(job)
        message = "Couldn't find any job called %s " % job
    elif not Build.query.filter_by(number=build).count():
        agent = Agent.query.one()
        conn = jenkins.Jenkins(agent.url, agent.user, agent.password)
        try:
            conn.get_build_info(job, build)
        except jenkins.NotFoundException:
            message = "Build not found"
            exists = False

    return jsonify(exists=exists, message=message)
