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
import logging

from rhoci.models import Agent
from rhoci.models import Build
from rhoci.models import Job


logger = logging.getLogger(__name__)

jobs = Blueprint('jobs', __name__)


@jobs.route('/')
def index():
    """Jenkins Jobs page."""
    jobs = Job.query.all()
    agent = Agent.query.one()

    return render_template('jobs.html', agent=agent, jobs=jobs)


@jobs.route('/jobs_status/<status>_<dfg>_<release>')
def jobs_status(status, dfg, release):
    """Get jobs with specific status"""
    results = dict()
    results['data'] = list()

    jobs = Job.query.filter(Job.name.contains('DFG-%s' % dfg),
                            Job.last_build_status.like(status),
                            Job.release_number.like(release))
    for job in jobs:
        if Build.query.filter_by(job=job.name,
                                 number=job.last_build_number).count():
            build_db = Build.query.filter_by(
                job=job.name,
                number=job.last_build_number).first()
            if build_db.failure_name:
                results['data'].append([job.name, build_db.failure_name,
                                        job.last_build_number,
                                        build_db.failure_text, ''])
            else:
                results['data'].append([job.name, job.last_build_status,
                                        job.last_build_number, ''])
        else:
            results['data'].append([job.name, job.last_build_status,
                                    job.last_build_number, ''])
    print results
    return jsonify(results)
