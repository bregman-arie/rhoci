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

from rhoci.models.job import Job

LOG = logging.getLogger(__name__)

from rhoci.api import bp  # noqa

PROJECTION = {'name': 1, 'last_build': 1, 'release': 1, 'last_successful_build': 1}


@bp.route('/jobs', methods=['GET', 'POST'])
def jobs(query_str=None):
    """All jobs API route."""
    q_str = request.args.get('query_str', default={})
    if q_str:
        query_str = eval(q_str)
    else:
        query_str = {}
    results = {'data': Job.find(query_str=query_str, projection=PROJECTION)}
    return jsonify(results)


@bp.route('/jobs/DFG=<DFG_name>')
@bp.route('/jobs/<job_name>')
@bp.route('/jobs/<DFG_name>/squad/<squad_name>')
@bp.route('/jobs/<DFG_name>/component/<component_name>')
def get_jobs(DFG_name=None, squad_name=None,
             component_name=None, job_name=None):
    """Returns jobs."""
    results = {'data': []}
    if squad_name:
        jobs = Job.find(squad=squad_name, projection=PROJECTION)
    elif component_name:
        jobs = Job.find(query_str={'DFG': DFG_name, 'component': component_name},
                        projection=PROJECTION)
    elif DFG_name:
        jobs = Job.find(name='DFG-{}'.format(DFG_name),
                        projection=PROJECTION)
    elif job_name:
        jobs = Job.find(name=job_name, exact_match=True,
                        projection=PROJECTION)
    for job in jobs:
        results['data'].append(job)
    return jsonify(results)
