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
from flask import current_app as app
from flask import jsonify
from flask import request
import json
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


@bp.route('/jobs/filtered', methods=['GET', 'POST'])
@bp.route('/jobs/filtered?filters=<filters>', methods=['GET', 'POST'])
def get_filtered_jobs(filters=None):
    filters = request.args.get('filters')
    if filters and filters != "undefined":
        filters_dict = json.loads(filters)
    else:
        filters_dict = {}
    results = {'data': []}
    es = Elasticsearch(app.config['custom']['elk']['es']['url'])
    body = {
        "query": {
            "bool": {}},
        "size": 0,
        "aggs": {
            "jobs": {
                "terms": {"field": "job_name.keyword",
                          "size": 1000},
                "aggs": {
                    "builds": {
                        "terms": {"field": "build_num"},
                        "aggs": {
                            "status": {
                                "terms": {"field": "build_result.keyword"}
                }
            }
        }}}}}
    if filters_dict:
        body["query"]["bool"]["filter"] = []
        filters_modified = {"{}.keyword".format(k):v for k,v in filters_dict.items()}
        for f,v in filters_modified.items():
            body["query"]["bool"]["filter"].append({ "term": {f:v} })
    res = es.search(index="logstash", body=body)
    for job in res['aggregations']['jobs']['buckets']:
        if job['builds']['buckets'] and job['builds']['buckets'][-1]['status']['buckets']:
            status = job['builds']['buckets'][-1]['status']['buckets'][-1]['key']
        else:
            status = "None"
        results['data'].append({'job_name': job['key'], 'build_number': int(job['builds']['buckets'][-1]['key']), 'status': status})
    return jsonify(results)



@bp.route('/jobs/<DFG_name>/<status>')
@bp.route('/jobs/DFG=<DFG_name>')
@bp.route('/jobs/<job_name>')
@bp.route('/jobs/all')
def get_jobs(DFG_name=None, squad_name=None,
             component_name=None, job_name=None, status=None):
    """Returns jobs."""
    jobs = defaultdict(dict)
    results = {'data': []}
    es = Elasticsearch(app.config['custom']['elk']['es']['url'])
    body = {
        "query": {
            "bool": {
                "must": [{"exists": {"field": "build_result.keyword"}} ],
                # "filter": [
                #    { "term": { "DFG.keyword": DFG_name}}
                #]
            }},
        "size": 0,
        "aggs": {
            "jobs": {
                "terms": {"field": "job_name.keyword",
                          "size": 1000},
                "aggs": {
                    "builds": {
                        "terms": {"field": "build_num"},
                        "aggs": {
                            "status": {
                                "terms": {"field": "build_result.keyword"}
                }
            }
        }}}}}
    if DFG_name and status:
        body["query"]["bool"]["filter"] = [{ "term": { "DFG.keyword": DFG_name}}]
        res = es.search(index="logstash", body=body)
        for job in res['aggregations']['jobs']['buckets']:
            if job['builds']['buckets'][-1]['status']['buckets'][-1]['key'] == status:
                results['data'].append({'job_name': job['key'], 'build_number': int(job['builds']['buckets'][-1]['key']), 'status': status})
    elif DFG_name:
        body["query"]["bool"]["filter"] = [{ "term": { "DFG.keyword": DFG_name}}]
        res = es.search(index="logstash", body=body)
        for job in res['aggregations']['jobs']['buckets']:
            results['data'].append({'job_name': job['key'], 'build_number': int(job['builds']['buckets'][-1]['key']), 'status': job['builds']['buckets'][-1]['status']['buckets'][-1]['key']})
    else:
        res = es.search(index="logstash", body=body)
        for job in res['aggregations']['jobs']['buckets']:
            results['data'].append({'job_name': job['key'], 'build_number': int(job['builds']['buckets'][-1]['key']), 'status': job['builds']['buckets'][-1]['status']['buckets'][-1]['key']})
    return jsonify(results)
