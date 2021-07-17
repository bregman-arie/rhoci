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
from flask import flash
from flask import jsonify
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
import logging
from werkzeug.urls import url_parse
import yaml

from rhoci.jenkins.osp import get_release
from rhoci.forms.login import Login
from rhoci.forms.register import Register
from rhoci.models.job import Job
from rhoci.models.DFG import DFG
from rhoci.models.user import User
import rhoci.jenkins.constants as jenkins_const

LOG = logging.getLogger(__name__)

from rhoci.main import bp  # noqa


def get_DFGs_result_summary(DFGs):
    """Given a list of DFG names, returns a dictionary with the
    summary of a given DFG CI jobs.
    DFGs_summary = {'Network': {'FAILED': 2,
                                'PASSED': 12},
                    'Compute': {'FAILED': 3,
                    ...
                   }
    """
    DFGs_summary = dict()
    for DFG_name in DFGs:
        DFGs_summary[DFG] = {}
        for res in jenkins_const.RESULTS:
            DFGs_summary[DFG_name][res] = Job.count(
                name='DFG-{}'.format(DFG_name),
                last_build_res=res)
    return DFGs_summary


@bp.route('/')
def index():
    """Main page route."""
    with open(r'/etc/arie.yaml') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)

    es = Elasticsearch(data['elk']['es_url'])
    body = {
        "size": 0,
        "aggs" : {
            "jobs" : {
                "terms" : { "field" : "osp_release.keyword",  "size" : 4000 }
            }
        }
    }
    result = es.search(index="logstash", body=body)
    releases = []
    for release in result["aggregations"]['jobs']['buckets']:
        uf = url_for('main.release_summary', release_number=release['key'])
        releases.append({'number': release['key'], 'doc_count': release['doc_count'],
                         'url_for': uf})

    DFGs_data = []
    all_DFGs = DFG.get_all_DFGs_based_on_jobs()
    for DFG_name in all_DFGs:
        uf = url_for('DFG.summary', DFG_name=DFG_name)
        failure_uf = url_for('DFG.builds_in_status', DFG_name=DFG_name, status='FAILURE')
        success_uf = url_for('DFG.builds_in_status', DFG_name=DFG_name, status='SUCCESS')
        unstable_uf = url_for('DFG.builds_in_status', DFG_name=DFG_name, status='UNSTABLE')
        DFGs_data.append({'name': DFG_name,
                          'summary_url_for': uf,
                          'failure_builds_uf': failure_uf,
                          'success_builds_uf': success_uf,
                          'unstable_builds_uf': unstable_uf,
                         })
    return render_template('index.html', title="releases", releases=releases, DFGs=DFGs_data)















@bp.route('/tests/<job_name>/<build_number>')
def get_tests(job_name, build_number):
    with open(r'/etc/arie.yaml') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    es = Elasticsearch(data['elk']['es_url'])
    body = {"query": {"bool": { "must": [{"exists": {"field": "tests.name.keyword"}}, {"match": {"job_name.keyword": job_name}}, {"match": {"build_num": build_number}}]}}, "size": 9000, "_source": ["tests"]} 
    res = es.search(index="logstash", body=body)
    results = {'data': []}
    for test in res['hits']['hits']:
        results['data'].append({'name': test['_source']['tests.name'], 'className': test['_source'].get('tests.classname'), 'status': test['_source']['tests.status'], 'duration': test['_source']['tests.time'] })
    return jsonify(results)


@bp.route('/job/<job_name>/<build_number>/tests')
def build_tests(job_name, build_number):
    uf = url_for('main.get_tests', job_name=job_name, build_number=build_number)
    return render_template('build_tests.html', uf=uf)

@bp.route('/puddle/<puddle_id>/builds')
def get_puddle_builds(puddle_id):
    jobs = defaultdict(dict)
    with open(r'/etc/arie.yaml') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    body = {"query": {"bool": { "must": [{"exists": {"field": "job_name.keyword"}}, {"match": {"core_puddle.keyword": puddle_id}}]}}, "size": 9000, "_source": ["job_name", "build_num"],  "aggs": { "jobs": { "terms": {"field": "job_name.keyword"}, "aggregations": {"builds": {"terms": { "field": "build_num" }}}}}}
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
                    jobs[job['key']] = {'job_name': job['key'], 'status': build_result, 'number': build['key']}
            else:
                jobs[job['key']] = {'job_name': job['key'], 'status': 'In Progress', 'number': build['key']}
    for job_name, value in jobs.items():
        results['data'].append(value)
    print(results)
    return jsonify(results)

@bp.route('/puddle/<puddle_id>')
def puddle_summary(puddle_id):
    uf = url_for('main.get_puddle_builds', puddle_id=puddle_id)
    return render_template('puddle_summary.html', uf=uf)


@bp.route('/release/<release_number>')
def release_summary(release_number):
    with open(r'/etc/arie.yaml') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)

    es = Elasticsearch(data['elk']['es_url'])
    body = {
        "size": 0,
        "aggs" : {
            "jobs" : {
                "terms" : {"field" : "core_puddle.keyword",
                           "size" : 4000 }
            }
        }
    }
    result = es.search(index="logstash", body=body)
    puddles = []
    for puddle in result["aggregations"]['jobs']['buckets']:
        body = {"query": {"match": {"core_puddle.keyword": puddle["key"]}}, "size": 1}
        job_res = es.search(index="logstash", body=body)
        body = {"query": {"bool": { "must": [{"exists": {"field": "osp_release.keyword"}}, {"match": {"job_name.keyword": job_res['hits']['hits'][0]['_source']['job_name']}}]}}, "size": 1}
        job_res = es.search(index="logstash", body=body)
        if job_res['hits']['hits'] and job_res['hits']['hits'][0]['_source']['osp_release'] == release_number:
            uf = url_for('main.puddle_summary', puddle_id=puddle['key'])
            puddles.append({'id': puddle['key'], 'url_for': uf})
    return render_template('release_summary.html', puddles=puddles)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = Login()
    if form.validate_on_submit():
        user = User.find_one(form.username.data)
        if user and User.check_password(user['password'], form.password.data):
            user_obj = User(user['username'])
            login_user(user_obj)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('main.index')
            return redirect(next_page)
        else:
            flash("Invalid username or password")
    return render_template('main/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = Register()
    return render_template('main/register.html', title='Register', form=form)
