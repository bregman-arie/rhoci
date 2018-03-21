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

from rhoci import models
import rhoci.jenkins.job as job_lib


logger = logging.getLogger(__name__)

jobs = Blueprint('jobs', __name__)


@jobs.route('/')
def index():
    """Jenkins Jobs page."""
    agent = models.Agent.query.one()

    return render_template('jobs.html', agent=agent, jobs=jobs)


@jobs.route('/all')
def all():
    """Jenkins Jobs page."""
    jobs = models.Job.query.all()
    results = dict()
    results['data'] = list()

    for job in jobs:
        results['data'].append([None, job.name, job.last_build_result,
                                job.last_build_number,
                                job.timestamp, ''])

    return jsonify(results)


@jobs.route('/jobs_status/<status>_<dfg>_<release>')
def jobs_status(status, dfg, release):
    """Get jobs with specific status"""
    results = dict()
    results['data'] = list()

    jobs = models.Job.query.filter(models.Job.name.contains('DFG-%s' % dfg),
                                   models.Job.last_build_result.like(status),
                                   models.Job.release_number.like(release))
    results = job_lib.construct_jobs_dictionary(jobs)

    return jsonify(results)


@jobs.route('/home_jobs_status/<dfg>_<result>_<release>_<failure_name>')
def get(dfg=None, result=None, release=None, failure_name=None):
    """Get jobs with specific status"""
    results = dict()
    results['data'] = list()

    if (dfg != 'null' and result != 'null'):
        jobs = models.Job.query.filter(
            models.Job.name.contains('DFG-%s' % dfg),
            models.Job.last_build_result.like(result))
    elif (release != 'null' and result != 'null'):
        jobs = models.Job.query.filter_by(release_number=release,
                                          last_build_result=result)
    elif failure_name != 'null':
        builds = models.Build.query.filter_by(failure_name=failure_name)
        j = set([i.job for i in builds])
        jobs = models.Job.query.filter(models.Job.name.in_(j)).filter(
            models.Job.last_build_result.like("FAILURE"))

    results = job_lib.construct_jobs_dictionary(jobs)

    return jsonify(results)


@jobs.route('/home_jobs_status/<dfg>')
def get_failed(dfg=None):
    """Get failed and aborted jobs of a given DFG"""
    results = dict()
    results['data'] = list()

    jobs = models.Job.query.filter(
        models.Job.name.contains('DFG-%s' % dfg),
        (models.Job.last_build_result.like("FAILURE") |
         models.Job.last_build_result.like("ABORTED")))
    results = job_lib.construct_jobs_dictionary(jobs)

    return jsonify(results)
