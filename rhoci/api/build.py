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
from rhoci.models.job import Job

LOG = logging.getLogger(__name__)

from rhoci.api import bp  # noqa


@bp.route('/builds/all')
def all_builds():
    """All builds API route."""
    results = {'data': []}
    jobs = Job.find()
    for job in jobs:
        for build in job['builds']:
            results['data'].append(build)
    return jsonify(results)


@bp.route('/job/<job_name>/builds')
def get_builds(job_name=None):
    """Return builds"""
    results = {'data': []}
    jobs = Job.find(name_regex=job_name)
    for job in jobs:
        for build in job['builds']:
            results['data'].append(build)
    print(results)
    return jsonify(results)


@bp.route('/jenkins_update', methods=['POST'])
def jenkins_update():
    """Handles update received from Jenkins."""
    json = request.get_json(silent=True)
    JenkinsAgent.classify_and_insert_to_db(json)
    return jsonify({'notification': 'UPDATE_COMPLETE'})
