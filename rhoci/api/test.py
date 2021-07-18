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

from elasticsearch import Elasticsearch
from flask import current_app as app
from flask import jsonify
import logging
import yaml

from rhoci.models.job import Job
from rhoci.jenkins.tests import get_tests as load_tests

LOG = logging.getLogger(__name__)

from rhoci.api import bp  # noqa


@bp.route('/tests')
def all_tests():
    """All builds API route."""
    results = {'data': []}
    es = Elasticsearch(app.config['custom']['elk']['es']['url'])
    body = {
        "query": {
            "bool": {
                "must": [{"exists": {"field": "tests.name.keyword"}} ],
            }},
        "size": 1000,
        "aggs": {
            "jobs": {
                "terms": {"field": "job_name.keyword",
                          "size": 1000},
                "aggs": {
                    "builds": {
                        "terms": {"field": "build_num"},
        }}}}}
    res = es.search(index="logstash", body=body)
    for test in res['hits']['hits']:
        if "tests.classname" in test['_source']:
            classname = test['_source']['tests.classname']
        else:
            classname = "None"
        results['data'].append({'name': test['_source']['tests.name'], 'className': classname, 'status': test['_source']['tests.status'].upper() })

    return jsonify(results)

@bp.route('/test_to_jobs/<class_name>/<test_name>')
def test_to_jobs(class_name=None, test_name=None):
    """All builds API route."""
    results = {'data': []}
    es = Elasticsearch(app.config['custom']['elk']['es']['url'])
    body = {
        "query": {
            "bool": {
                "must": [{"exists": {"field": "tests.name.keyword"}} ],
            }},
        "size": 1000,
        "aggs": {
            "jobs": {
                "terms": {"field": "job_name.keyword",
                          "size": 1000},
                "aggs": {
                    "builds": {
                        "terms": {"field": "build_num"},
        }}}}}
    body["query"]["bool"]["filter"] = [{ "term": { "tests.name.keyword": test_name}}]
    res = es.search(index="logstash", body=body)
    for test in res['hits']['hits']:
        results['data'].append({'job_name': test['_source']['job_name'], 'build_number': test['_source']['build_num'], 'status': test['_source']['tests.status'].upper() })
    return jsonify(results)
