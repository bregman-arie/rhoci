# Copyright 2019 Arie Bregman
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
from __future__ import absolute_import

from flask import jsonify
from flask import request
import logging

from rhoci.jenkins.agent import JenkinsAgent
from rhoci.models.build import Build
from rhoci.models.job import Job

LOG = logging.getLogger(__name__)

from rhoci.api import bp  # noqa


@bp.route('/builds/all')
def all_builds():
    """All builds API route."""
    results = {'data': []}
    builds = Build.find()
    for build in builds:
        print(build)
        results['data'].append([build['job_name'], build['result'],
                               build['number'], build['date'],
                               ''])
    return jsonify(results)


@bp.route('/builds/<DFG_name>/<result>')
def get_builds(DFG_name, result):
    """Return builds based on DFG and result parameters."""
    results = {'data': []}
    jobs = Job.find(name_regex='DFG-{}'.format(DFG_name),
                    last_build_result=result)
    for job in jobs:
        lb = job['last_build']
        results['data'].append([job['name'], lb['result'],
                                lb['number'], lb['timestamp'], ''])
    return jsonify(results)


@bp.route('/jenkins_update', methods=['POST'])
def jenkins_update():
    """Handles update received from Jenkins."""
    json = request.get_json(silent=True)
    JenkinsAgent.classify_and_insert_to_db(json)
    return jsonify({'notification': 'UPDATE_COMPLETE'})
