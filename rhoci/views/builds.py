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

import rhoci.jenkins.build as build_lib
import rhoci.jenkins.job as jenkins_job
from rhoci import models
from rhoci.common.failures import UNKNOWN_FAILURE


LOG = logging.getLogger(__name__)

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

    db_builds = models.Build.query.filter_by(active=True)
    builds = [build.serialize for build in db_builds]
    agent = models.Agent.query.one()

    return render_template('active_builds.html', agent=agent, builds=builds)


@builds.route('/builds', methods=['GET'])
def all_builds():

    db_builds = models.Build.query.all()
    all_builds = [build.serialize for build in db_builds]

    return render_template('builds.html', all_builds=all_builds)


@builds.route('/exists/')
def exists():
    exists = True
    known_failure = False
    message = ''
    job = request.args.get('job')
    build = request.args.get('build')

    if not job or not build:
        exists = False
        message = "Invalid input"
    elif not models.Job.query.filter_by(name=job).count():
        exists, message = jenkins_job.exists(job)
        jenkins_job.add_new_job(job)
    elif not models.Build.query.filter_by(job=job, number=int(build)).count():
        agent = models.Agent.query.one()
        conn = jenkins.Jenkins(agent.url, agent.user, agent.password)
        try:
            conn.get_build_info(job, int(build))
        except jenkins.NotFoundException:
            message = "Build not found"
            exists = False

    if exists:
        if models.Build.query.filter_by(job=job, number=int(build)).count():
            build_db = models.Build.query.filter_by(
                job=job, number=int(build)).first()
            build_status = build_db.status
            if build_db.failure_name:
                known_failure = True
        else:
            build_status = build_lib.get_build_status(conn, job, int(build))
            build_lib.add_new_build(job, build)

        if build_status != "FAILURE":
            exists = False
            message = "The build didn't fail..."

    if known_failure:
        failure = models.Failure.query.filter_by(
            name=build_db.failure_name).first()
        return jsonify(exists=exists,
                       known_failure=known_failure,
                       cause=failure.cause,
                       action=failure.action,
                       failure_line=build_db.failure_text)
    else:
        return jsonify(exists=exists, message=message,
                       known_failure=known_failure)


@builds.route('/top_failure_types', methods=['GET'])
def top_failure_types():

    results = dict()
    results['data'] = list()

    db_failures = models.Failure.query.order_by(
        models.Failure.count.desc()).limit(7).all()

    for failure in db_failures:
        if failure.count:
            results['data'].append(
                [failure.name, failure.category, failure.count])

    return jsonify(results)


@builds.route('/get_failure')
def get_failure():
    job = request.args.get('job')
    build = request.args.get('build')

    build_db = models.Build.query.filter_by(job=job, number=build).first()
    failure_text = build_db.failure_text
    failure = models.Failure.query.filter_by(
        name=build_db.failure_name).first()
    if not failure:
        failure = UNKNOWN_FAILURE
        failure_text = failure.failure_text

    return jsonify(failure_name=failure.name,
                   failure_text=failure_text,
                   failure_action=failure.action,
                   failure_cause=failure.cause)


@builds.route('/analyze_failure')
def analyze_failure():
    """Try to find out why a given build failed."""
    # Set build and job according to passed parameters
    failure_name = "unknown"
    job = request.args.get('job')
    build = request.args.get('build')

    LOG.debug("Obtaining log files names for job %s build %s" % (job, build))
    logs = build_lib.get_log_files_names(job, build)

    if logs:
        LOG.debug("Looking for failure in logs for job %s build %s" % (
            job, build))
        failure_name = build_lib.find_failure_in_logs(logs, job, build)
    if failure_name == "unknown":
        LOG.debug("Looking for failure in console output for "
                  "job {} build {} since "
                  "I couldn't find anything in the logs".format(job, build))
        failure_name = build_lib.find_failure_in_console_output(job, build)

    return jsonify(failure_name=failure_name)
