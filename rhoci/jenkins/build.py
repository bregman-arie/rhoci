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
from urllib import urlopen

from rhoci.models import Artifact
from rhoci.models import Build
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
    return str(conn.get_build_info(job_name, build_number)['result'])


def get_artifacts(conn, job, build):
    build_db = Build.query.filter_by(job=job, number=build)
    print build_db.artifacts


def update_tests(tests_data, job, build_number):
    """Checks if build ran tests. If yes, updates DB with the tests."""
    #  TODO(abregman): move this code to python-jenkins
    for test in json.loads(tests_data)['suites'][0]['cases']:
        if not Test.query.filter_by(class_name=test['className']).count():
            test_db = Test(class_name=test['className'],
                           failure=0,
                           success=0)
            db.session.add(test_db)
            db.session.commit()
            LOG.debug("Added test %s" % test['className'])
        if not TestBuild.query.filter_by(class_name=test['className'],
                                         job=job, build=build_number).count():
            test_build_db = TestBuild(job=job, build=build_number,
                                      status=test['status'],
                                      skipped=test['skipped'],
                                      class_name=test['className'],
                                      name=test['name'],
                                      duration=test['duration'],
                                      errorStackTrace=test['errorStackTrace'])
            db.session.add(test_build_db)
            db.session.commit()
            LOG.debug("Added test build %s %s %s" % (test['className'], job,
                                                     build_number))
        if test['status'] == 'PASSED':
            Test.query.filter_by(class_name=test['className']).update(dict(
                success=+1))
        else:
            Test.query.filter_by(class_name=test['className']).update(dict(
                failure=+1))
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
    if 'artifcats' in data:
        artifacts = [i['archive'] for i in (
            [j for i, j in data['artifacts'].iteritems()])]
    else:
        artifacts = ''

    if not Build.query.filter_by(job=name, number=number).count():
        build = Build(job=name, number=number, status=status, active=active,
                      parameters=parameters, url=full_url, trigger=trigger)
        db.session.add(build)
        db.session.commit()

    if phase == 'finalized':
        status = data['build']['status']
        Build.query.filter_by(job=name, number=number).update(dict(
            active=active, status=status, artifacts=str(artifacts)))
        Job.query.filter_by(name=name).update(dict(last_build_number=number,
                                                   last_build_status=status))
        db.session.commit()
        url = current_app.config.get("url")
        tests_raw_data = urlopen(
            url + "/job/" + name + "/" +
            str(number) + "/testReport/api/json").read(
        )
        if 'Not found' not in tests_raw_data:
            LOG.debug("Found tests. Adding them to DB.")
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
    for art in artifacts:
        db_artifact = Artifact(name=art['fileName'],
                               build=int(build),
                               job=job,
                               relativePath=art['relativePath'])
        db.session.add(db_artifact)
        db.session.commit()
        LOG.info("Added artifact in DB: %s" % art['fileName'])
