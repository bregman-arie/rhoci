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

from collections import defaultdict
from elasticsearch import Elasticsearch
from flask import jsonify
from flask import request
import yaml

import logging

from rhoci.models.job import Job
from rhoci.jenkins.osp import get_release

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
    jobs = defaultdict(dict)
    if squad_name:
        jobs = Job.find(squad=squad_name, projection=PROJECTION)
    elif component_name:
        jobs = Job.find(query_str={'DFG': DFG_name, 'component': component_name},
                        projection=PROJECTION)
    elif DFG_name:
        with open(r'/etc/arie.yaml') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        body = {"query": {"bool": { "must": [{"exists": {"field": "job_name.keyword"}}, {"match": {"DFG.keyword": DFG_name}}]}}, "size": 9000, "_source": ["job_name", "build_num"],  "aggs": { "jobs": { "terms": {"field": "job_name.keyword"}, "aggregations": {"builds": {"terms": { "field": "build_num" }}}}}}
        es = Elasticsearch(data['elk']['es_url'])
        res = es.search(index="logstash", body=body)
        results = {'data': []}
        for job in res['aggregations']['jobs']['buckets']:
            for build in job['builds']['buckets']:
                body = {"query": {"bool": { "must": [{"exists": {"field": "build_result.keyword"}}, {"match": {"job_name.keyword": job['key']}}, {"match": {"build_num": build['key']}}]}}, "size": 9000, "_source": ["job_name", "build_num", "build_result"]}
                builds_res = es.search(index="logstash", body=body)
                if builds_res['hits']['hits']:
                    for build_res in builds_res['hits']['hits']:
                        build_result = build_res['_source']['build_result']
                        if job['key'] in jobs:
                            if build['key'] > jobs[job['key']]['last_build']['number']:
                                jobs[job['key']]['last_build'] = {'number': build['key'], 'status': build_result, 'name': job['key']}
                            elif build_result == "SUCCESS" and build['key'] > jobs[job['key']]['last_successful_build']['number']:
                                jobs[job['key']]['last_successful_build'] = {'number': build['key'], 'status': build_result, 'name': job['key']}
                        else:
                            jobs[job['key']] = {'name': job['key'], 'release': get_release(job['key']), 'last_build': {'number': build['key'], 'status': build_result, 'name': job['key']}}
                            if build_result == "SUCCESS":
                                jobs[job['key']]['last_successful_build'] = {'number': build['key'], 'status': build_result, 'name': job['key']}
    elif job_name:
        jobs = Job.find(name=job_name, exact_match=True,
                        projection=PROJECTION)
    for job_name, value in jobs.items():
        results['data'].append(value)
    return jsonify(results)
