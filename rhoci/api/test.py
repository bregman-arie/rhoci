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
import logging

from rhoci.models.job import Job
from rhoci.jenkins.tests import get_tests as load_tests

LOG = logging.getLogger(__name__)

from rhoci.api import bp  # noqa


@bp.route('/tests')
def all_tests():
    """All builds API route."""
    results = {'data': []}
    jobs = Job.find()
    for job in jobs:
        for build in job['builds']:
            if 'tests' in build:
                for test in build['tests']:
                    results['data'].append(test)
    return jsonify(results)


@bp.route('/job/<job_name>/<build_number>/tests')
def get_tests(job_name=None, build_number=None):
    """Return builds"""
    results = {'data': []}
    job = Job.find(job_name, build_number=int(build_number), exact_match=True,
                   projection={'builds.$.tests': 1, '_id': 0})
    if 'tests' in job[0]['builds'][0]:
        tests = job[0]['builds'][0]['tests']
    else:
        tests = load_tests(job=job_name, build=build_number)
    results = {'data': tests}
    return jsonify(results)
