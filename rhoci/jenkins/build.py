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
from flask import current_app
import json
import jenkins
import logging
import urllib2

from rhoci.models import Agent
from rhoci.models import Artifact
from rhoci.models import Build
from rhoci.models import Failure
from rhoci.models import Job
from rhoci.models import Test
from rhoci.models import TestBuild
from rhoci.db.base import db

LOG = logging.getLogger(__name__)


def get_last_build_number(job_info):
    """Given a job info dict, returns the last build number."""
    if job_info['lastCompletedBuild']:
        return job_info['lastCompletedBuild']['number']
    else:
        return 0


def get_build_status(conn, job_name, build_number):
    """Given a Jenkins connection and job name, it returns string of

    the last completed build result.
    """
    return str(conn.get_build_info(job_name, int(build_number))['result'])


def update_failure(job, number, failure_name, text):
    """Update the failure cause of a specific build."""
    Build.query.filter_by(job=job, number=int(number)).update(
        dict(failure_text=unicode(text, 'utf-8'), failure_name=failure_name))
    db.session.commit()


def update_tests(tests_data, job, build):
    """Checks if build ran tests. If yes, updates DB with the tests."""
    #  TODO(abregman): move this code to python-jenkins
    LOG.info("Adding tests to DB for job %s build %s" % (job, build))
    for test in json.loads(tests_data)['suites'][0]['cases']:
        # Avoid setUpClass
        if test['className'] != '':
            if not Test.query.filter_by(class_name=test['className']).count():
                test_db = Test(class_name=test['className'],
                               failure=0,
                               success=0)
                db.session.add(test_db)
                db.session.commit()
                LOG.debug("Added test %s" % test['className'])
            if (not TestBuild.query.filter_by(class_name=test['className'],
                                              job=job, build=build).count()):
                test_build_db = TestBuild(job=job, build=build,
                                          status=test['status'],
                                          skipped=test['skipped'],
                                          class_name=test['className'],
                                          name=test['name'],
                                          duration=test['duration'],
                                          errorStackTrace=test[
                                              'errorStackTrace'])
                db.session.add(test_build_db)
                db.session.commit()
                LOG.debug("Added test build %s %s %s" % (test['className'], job,
                                                         build))
            if test['status'] == 'PASSED':
                Test.query.filter_by(class_name=test['className']).update(
                    {'success': Test.success + 1})
            else:
                Test.query.filter_by(class_name=test['className']).update(
                    {'failure': Test.failure + 1})
            db.session.commit()


def add_new_build(job, number):
    """Add a new build to the DB."""

    agent = Agent.query.one()
    conn = jenkins.Jenkins(agent.url, agent.user, agent.password)
    status = get_build_status(conn, job, number)
    build = Build(job=job, number=number, status=status)
    db.session.add(build)
    db.session.commit()


def update_in_db(data):
    """Update builds table with given data."""
    active = False
    status = trigger = "Unknown"
    phase = (data['build']['phase']).lower()
    parameters = str(data['build']['parameters'])
    full_url = data['build']['full_url']
    name = data['name']
    number = data['build']['number']

    if data['build']['phase'] == 'STARTED':
        active = True
        status = 'IN_PROGRESS'
        # TODO(abregman): Very inefficient. Jenkins notifications plugin
        #                 should send this information.
        if 'GERRIT_EVENT_ACCOUNT_NAME' in data['build']['parameters']:
            trigger = "Gerrit (%s)" % data[
                'build']['parameters']['GERRIT_EVENT_ACCOUNT_NAME']
        else:
            try:
                conn = jenkins.Jenkins(current_app.config.get('url'),
                                       current_app.config.get('user'),
                                       current_app.config.get('password'))
                build_info = conn.get_build_info(name, number)
                trigger = build_info[
                    'actions'][1]['causes'][0]['shortDescription']
            except Exception as e:
                LOG.info("Was unable to get build info: %s" % e.message)
    # todo(abregman): Add artifacts to the DB
    # if 'artifcats' in data:

    if not Build.query.filter_by(job=name, number=number).count():
        build = Build(job=name, number=number, status=status, active=active,
                      parameters=parameters, url=full_url, trigger=trigger)
        db.session.add(build)
        db.session.commit()

    if phase == 'finalized':
        status = data['build']['status']
        Build.query.filter_by(job=name, number=number).update(dict(
            active=active, status=status))
        Job.query.filter_by(name=name).update(dict(last_build_number=number,
                                                   last_build_status=status))
        db.session.commit()
        url = current_app.config.get("url")
        tests_raw_data = urllib2.urlopen(
            url + "/job/" + name + "/" +
            str(number) + "/testReport/api/json").read()
        if 'Not found' not in tests_raw_data:
            update_tests(tests_raw_data, name, number)


def check_active_builds(conn):
    """Checks if active builds in DB are indeed still active."""
    active_builds_db = Build.query.filter_by(active=True).all()
    for build in active_builds_db:
        try:
            conn.get_build_info(build.job, build.number)
        except jenkins.NotFoundException:
            LOG.info("Couldn't find build. Job is removed from Jenkins.")
            job = Job.query.filter_by(name=build.job).first()
            db.session.delete(job)
            db.session.delete(build)
            db.session.commit()
            LOG.info("Removed job and build.")


def update_artifacts_db(artifacts, job, build):
    logs = []
    for art in artifacts:
        if art['fileName'].endswith(".log"):
            logs.append(art['fileName'])
        db_artifact = Artifact(name=art['fileName'],
                               build=int(build),
                               job=job,
                               relativePath=art['relativePath'])
        db.session.add(db_artifact)
        db.session.commit()
        LOG.info("Added artifact in DB: %s" % art['fileName'])
    return logs


def get_artifacts(job, build):
    """Obtain the name the artifacts of a given build and update the DB

    accordingly.
    """
    if not Artifact.query.filter_by(job=job, build=int(build)).count():
        agent = Agent.query.one()
        conn = jenkins.Jenkins(agent.url, agent.user, agent.password)
        artifacts = conn.get_build_info(job, int(build))['artifacts']
        update_artifacts_db(artifacts, job, build)


def check_match(data):
    """Simple comparison to find out if there is a match."""
    for line in data:
        if line:
            for failure in Failure.query.all():
                if failure.pattern in line.decode('utf-8').strip():
                    Failure.query.filter_by(name=failure.name).update(
                        {'count': Failure.count + 1})
                    db.session.commit()
                    return True, line, failure.name
    return False, '', ''


def analyze_failure(job, build):
    """Tries to figure out why a certain build failed and updates the

    DB accordingly.
    """
    found = False
    match = False
    get_artifacts(job, build)
    agent = Agent.query.one()

    # Check if there are artifacts that end with .log
    logs = [i for i in Artifact.query.filter_by(
        job=job, build=int(build)) if i.name.endswith(".log")]

    if logs:
        for log in logs:
            if found:
                break
            log_url = "{}/job/{}/{}/artifact/{}".format(agent.url, job, build,
                                                        str(log.relativePath))
            try:
                log_data = urllib2.urlopen(log_url)
                match, failure_text, failure_name = check_match(log_data)
                if match:
                    update_failure(job, build, failure_name, failure_text)
                    break
            except urllib2.HTTPError:
                LOG.debug("Couldnt read logs for job %s build %s." % (
                    job, build))
        if not match:
            console_url = "{}/job/{}/{}/consoleText".format(str(agent.url),
                                                            str(job),
                                                            str(build))
            console_data = urllib2.urlopen(console_url)
            match, failure_text, failure_name = check_match(console_data)
            if match:
                update_failure(job, build, failure_name, failure_text)
        if not match:
                LOG.info("Was unable to figure out " +
                         "why job %s build %s failed" % (job, build))
                update_failure(job, build, 'Unknown', '')
        else:
            LOG.info("The failure for job %s build %s is %s" % (job, build,
                                                                failure_name))
    else:
        console_url = "{}/job/{}/{}/consoleText".format(str(agent.url),
                                                        str(job),
                                                        str(build))
        console_data = urllib2.urlopen(console_url)
        match, failure_text, failure_name = check_match(console_data)
        if match:
            update_failure(job, build, failure_name, failure_text)
        else:
            LOG.info("Was unable to figure out " +
                     "why job %s build %s failed" % (job, build))
