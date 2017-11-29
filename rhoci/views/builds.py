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
import urllib2

from rhoci.db.base import db
import rhoci.jenkins.build as jenkins_build
import rhoci.jenkins.job as jenkins_job
from rhoci.models import Agent
from rhoci.models import Artifact
from rhoci.models import Build
from rhoci.models import Failure
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
@builds.route('/failure_anaylze/<job>_<build>', methods=['GET'])
def failure_analyze(job=None, build=None):

    if job:
        return render_template('start_failure_analyzer.html', job=job,
                               build=build)
    else:
        return render_template('failure_analyzer.html')


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
    elif not Job.query.filter_by(name=job).count():
        exists, message = jenkins_job.exists(job)
        jenkins_job.add_new_job(job)
    elif not Build.query.filter_by(job=job, number=int(build)).count():
        agent = Agent.query.one()
        conn = jenkins.Jenkins(agent.url, agent.user, agent.password)
        try:
            conn.get_build_info(job, int(build))
        except jenkins.NotFoundException:
            message = "Build not found"
            exists = False

    if exists:
        if Build.query.filter_by(job=job, number=int(build)).count():
            build_db = Build.query.filter_by(
                job=job, number=int(build)).first()
            build_status = build_db.status
            if build_db.failure_name:
                known_failure = True
        else:
            build_status = jenkins_build.get_build_status(conn,
                                                          job, int(build))
            jenkins_build.add_new_build(job, build)

        if build_status != "FAILURE":
            exists = False
            message = "The build didn't fail..."

    if known_failure:
        failure = Failure.query.filter_by(name=build_db.failure_name).first()
        return jsonify(exists=exists,
                       known_failure=known_failure,
                       cause=failure.cause,
                       action=failure.action,
                       failure_line=build_db.failure_text)
    else:
        return jsonify(exists=exists, message=message,
                       known_failure=known_failure)


@builds.route('/obtain_logs')
def obtain_logs():
    found = False
    message = "Couldn't find logs :("

    job = request.args.get('job')
    build = request.args.get('build')

    agent = Agent.query.one()
    conn = jenkins.Jenkins(agent.url, agent.user, agent.password)
    if Artifact.query.filter_by(job=job, build=int(build)).count():
        logs = [str(i.name) for i in Artifact.query.filter_by(
            job=job, build=int(build)) if i.name.endswith(".log")]
        found = True
        message = "Found logs in DB"
    else:
        logs = conn.get_build_info(job, int(build))['artifacts']
        if logs:
            jenkins_build.update_artifacts_db(logs, job, build)
            found = True
            message = "Found logs in Jenkins"
        logs = [str(i.name) for i in Artifact.query.filter_by(
            job=job, build=int(build)) if i.name.endswith(".log")]

    return jsonify(found=found, message=message, logs=logs)


@builds.route('/find_failure')
def find_failure():
    found = False
    cause = ''
    action = ''
    failure_line = ''

    job = request.args.get('job')
    build = request.args.get('build')

    agent = Agent.query.one()
    logs = [i for i in Artifact.query.filter_by(
        job=job, build=int(build)) if i.name.endswith(".log")]

    if logs:
        for log in logs:
            if found:
                break
            log_url = "{}/job/{}/{}/artifact/{}".format(agent.url, job, build,
                                                        str(log.relativePath))
            log_data = urllib2.urlopen(log_url)
            for line in log_data:
                for failure in Failure.query.all():
                    if failure.pattern in line.decode('utf-8').strip():
                        found = True
                        failure_line = line
                        cause = failure.cause
                        action = failure.action
                        failure_name = failure.name
                        Failure.query.filter_by(
                            name=failure.name).update(
                                {'count': Failure.count + 1})
                        db.session.commit()
                        break
    else:
        console_url = "{}/job/{}/{}/consoleText".format(str(agent.url),
                                                        str(job), str(build))
        console_data = urllib2.urlopen(console_url)
        for line in console_data:
            if found:
                break
            for failure in Failure.query.all():
                if failure.pattern in line.decode('utf-8').strip():
                    found = True
                    failure_line = line
                    cause = failure.cause
                    action = failure.action
                    failure_name = failure.name
                    Failure.query.filter_by(
                        name=failure.name).update(
                            {'count': Failure.count + 1})
                    db.session.commit()
                    break

    if found:
        jenkins_build.update_failure(job, build, failure_name, failure_line)

    return jsonify(found=found, failure_line=failure_line,
                   cause=cause, action=action)


@builds.route('/top_failure_types', methods=['GET'])
def top_failure_types():

    results = dict()
    results['data'] = list()

    db_failures = Failure.query.order_by(Failure.count.desc()).limit(5).all()

    for failure in db_failures:
        if failure.count:
            results['data'].append(
                [failure.name, failure.category, failure.count])

    return jsonify(results)


@builds.route('/get_failure')
def get_failure():
    job = request.args.get('job')
    build = request.args.get('build')

    build_db = Build.query.filter_by(job=job, number=build).first()
    failure = Failure.query.filter_by(name=build_db.failure_name).first()

    return jsonify(failure_name=failure.name,
                   failure_text=build_db.failure_text,
                   failure_action=failure.action,
                   failure_cause=failure.cause)
