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
from jenkins import NotFoundException
import logging

from rhoci.models import Build
from rhoci.models import Job
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


def update_in_db(data):
    """Update builds table with given data."""
    active = False
    trigger = "Unknown"
    phase = (data['build']['phase']).lower()
    parameters = str(data['build']['parameters'])
    full_url = data['build']['full_url']
    name = data['name']
    number = data['build']['number']

    if data['build']['phase'] == 'STARTED':
        active = True
        status = 'IN_PROGRESS'
    if 'artifcats' in data:
        artifacts = [i['archive'] for i in (
            [j for i, j in data['artifacts'].iteritems()])]
    else:
        artifacts = ''
    if 'GERRIT_EVENT_ACCOUNT_NAME' in data['build']['parameters']:
        trigger = "Gerrit (%s)" % data[
            'build']['parameters']['GERRIT_EVENT_ACCOUNT_NAME']

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


def check_active_builds(conn):
    """Checks if active builds in DB are indeed still active."""
    active_builds_db = Build.query.filter_by(active=True).all()
    for build in active_builds_db:
        try:
            build_info = conn.get_build_info(build.job, build.number)
            print build_info
        except NotFoundException:
            LOG.info("Couldn't find build. Job is removed from Jenkins.")
            job = Job.query.filter_by(name=build.job).first()
            db.session.delete(job)
            db.session.delete(build)
            db.session.commit()
            LOG.info("Removed job and build.")
