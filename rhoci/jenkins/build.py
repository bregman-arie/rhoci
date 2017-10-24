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
from rhoci.models import Build
from rhoci.db.base import db


def get_last_build_number(job_info):
    """Given a job info dict, returns the last build number."""
    if job_info['lastCompletedBuild']:
        return job_info['lastCompletedBuild']['number']
    else:
        return 0


def get_build_result(conn, job_name, build_number):
    """Given a Jenkins connection and job name, it returns string of

    the last completed build result.
    """
    return str(conn.get_build_info(job_name, build_number)['result'])


def update_in_db(data):
    """Update builds table with given data."""
    active = True if data['build']['phase'] != 'COMPLETED' else False
    name = data['name']
    number = data['build']['number']
    phase = (data['build']['phase']).lower()

    if not Build.query.filter_by(job=name, number=number).count():
        build = Build(job=name, number=number, active=active)
        db.session.add(build)
        db.session.commit()

    if phase == 'completed':
        Build.query.filter_by(job=name, number=number).update(dict(
            active=False, status=data['build']['status']))
