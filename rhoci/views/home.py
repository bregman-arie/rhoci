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
from flask import jsonify
from flask import request
import logging

import rhoci.agent.update as agent_update
from rhoci.jenkins import manager
from rhoci.models import Build
from rhoci.models import Agent
from rhoci.views.doc import auto
from rhoci.models import Job
from rhoci.models import Release
from rhoci.models import TestBuild

LOG = logging.getLogger(__name__)

home = Blueprint('home', __name__)


@home.route('/')
def index():
    """Home page."""
    releases = Release.query.all()
    jobs = {}
    jobs['phase1'] = Job.query.filter_by(job_type='phase1')
    jobs['phase2'] = Job.query.filter_by(job_type='phase2')
    jobs['dfg'] = Job.query.filter_by(job_type='dfg')
    agent = Agent.query.one()

    return render_template('home.html',
                           releases=releases,
                           agent=agent,
                           phase1=jobs['phase1'],
                           phase2=jobs['phase2'],
                           dfg=jobs['dfg'])


@home.route('/releases/ajax/jobs/<job_type>_<release>')
def ajax_jobs(job_type, release):

    results = dict()
    results['data'] = list()

    jobs = Job.query.filter_by(job_type=job_type, release_number=int(release))

    for job in jobs:
        results['data'].append([job.name, job.last_build_status,
                                job.last_build_number])

    return jsonify(results)


@auto.doc(groups=['jobs', 'public'])
@home.route('/v2.0/jobs', methods=['GET', 'POST'])
def list_jobs():
    """Returns all jobs in the DB."""
    if request.method == 'POST':
        job = Job.query.filter_by(
            name=request.form['job_name']).first()
        jobs = job.serialize if job else {}
    else:
        jobs = [i.serialize for i in Job.query.all()]

    return jsonify(output=jobs)


@auto.doc(groups=['jobs', 'public'])
@home.route('/v2.0/jobs/<string:job_name>', methods=['GET', 'DELETE'])
def get_job(job_name):
    """Returns data on a specific job."""
    job = Job.query.filter_by(name=job_name).all()
    if job:
        if request.method == 'DELETE':
            agent_update.job_db_delete(job_name)
            return jsonify({'job name:': job_name,
                            'status': 'removed'})
        else:
            return jsonify(job[0].serialize)
    else:
        return jsonify({'exist': False})


@auto.doc(groups=['tests', 'public'])
@home.route('/v2.0/tests', methods=['GET', 'POST'])
def list_tests():
    """Returns all tests in the DB."""
    if request.method == 'POST':
        tests = TestBuild.query.filter_by(job_name=request.form['job_name'],
                                          build_number=request.form[
                                              'build_number']).all()
    else:
        tests = [i.serialize for i in TestBuild.query.all()]

    return jsonify(tests=tests)


@auto.doc(groups=['update', 'public'])
@home.route('/v2.0/update_jobs', methods=['GET', 'POST'])
def update_jobs():
    """Shallow update of all jobs."""
    LOG.info("Jobs update requested.")
    agent_update.shallow_jobs_update()
    return jsonify({'status': 'OK'})


@home.route('/v2.0/jenkins_notifications', methods=['POST'])
def jenkins_notifications():
    """Recieving notifications from Jenkins."""
    LOG.info("Recieved notification from Jenkins.")
    LOG.debug("Data: %s" % request.data)
    status = manager.update_db(request.get_json(silent=True))
    return jsonify({'notification': status})


@auto.doc(groups=['builds', 'public'])
@home.route('/v2.0/builds', methods=['GET', 'POST'])
def builds():
    """Returns information on Jenkins builds."""
    builds = [i.serialize for i in Build.query.all()]
    return jsonify(builds=builds)
