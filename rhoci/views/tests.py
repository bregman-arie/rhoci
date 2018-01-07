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
from flask import redirect
from flask import request
import logging
import urllib2

import rhoci.models as models
import rhoci.jenkins.build as jenkins_build


logger = logging.getLogger(__name__)

tests = Blueprint('tests', __name__)


@tests.route('/test_runs', methods=['GET'])
def test_runs():

    db_tests = models.TestBuild.query.all()
    all_tests = [test.serialize for test in db_tests]

    return render_template('tests.html', all_tests=all_tests)


@tests.route('/unique_tests', methods=['GET'])
def unique_tests():

    db_tests = models.Test.query.all()
    all_tests = [test.serialize for test in db_tests]

    return render_template('unique_tests.html', all_tests=all_tests)


@tests.route('/top_failing_tests', methods=['GET'])
def top_failing_tests():

    results = dict()
    results['data'] = list()

    db_tests = models.Test.query.order_by(
        models.Test.failure.desc()).filter(models.Test.failure > 0).limit(
            5).all()

    for test in db_tests:
        results['data'].append([test.class_name, test.test_name,
                                test.failure])

    return jsonify(results)


@tests.route('/get_tests/<job>_<build>', methods=['GET'])
def get_tests(job=None, build=None):

    agent = models.Agent.query.one()

    if models.TestBuild.query.filter_by(job=job, build=build).count():

        tests = models.TestBuild.query.filter_by(job=job, build=build).all()
        return render_template('tests.html', all_tests=tests)

    else:

        tests_raw_data = urllib2.urlopen(agent.url + "/job/" + job + "/" +
                                         build + "/testReport/api/json").read()
        if 'Not found' not in tests_raw_data:
            jenkins_build.update_tests(tests_raw_data, job, build)

        tests_url = agent.url + '/job/' + job + '/' + build + '/testReport'
        return redirect(tests_url)


@tests.route('/get_tests_datatable/<job>_<build>', methods=['GET'])
@tests.route('/get_tests_datatable/', methods=['GET'])
def get_tests_datatable(job=None, build=None):

    results = dict()
    results['data'] = list()
    agent = models.Agent.query.one()
    if not job:
        job = request.args.get('job')
        build = request.args.get('build')

    if models.TestBuild.query.filter_by(job=job, build=build).count():
        tests = models.TestBuild.query.filter_by(job=job, build=build).all()
        for test in tests:
            results['data'].append([test.class_name, test.name, test.status])
        return jsonify(results)
    else:
        try:
            tests_raw_data = urllib2.urlopen(agent.url + "/job/" + job + "/" +
                                             build +
                                             "/testReport/api/json").read()
            if 'Not found' not in tests_raw_data:
                jenkins_build.update_tests(tests_raw_data, job, build)
            tests = models.TestBuild.query.filter_by(
                job=job, build=build).all()
            for test in tests:
                results['data'].append([test.class_name, test.name,
                                        test.status, '',
                                        [i.serialize for i in test.bugs]])
        except urllib2.HTTPError:
                results['data'].append(["No tests", "No tests", "No tests",
                                        "No tests", "No tests"])

        return jsonify(results)


@tests.route('/failing_tests_dfg/<dfg>')
def failing_tests_dfg(dfg):
    """Get all the failed tests for a given DFG."""
    results = dict()
    results['data'] = list()

    tests = models.TestBuild.query.filter(models.TestBuild.job.contains(
        'DFG-%s' % dfg),
        (models.TestBuild.status.like('FAILED') | models.TestBuild.status.like(
            'REGRESSION'))).distinct(models.TestBuild.job).distinct(
                models.TestBuild.build)

    if tests:
        for test in tests:
            unique_test = models.Test.query.filter_by(
                test_name=test.name, class_name=test.class_name).first()
            if not unique_test:
                jenkins_build.add_unique_test(test.name, test.class_name,
                                              test.status)
                bugs = []
            else:
                bugs = unique_test.bugs

            results['data'].append([test.class_name, test.name, test.job,
                                    test.build, test.status,
                                    [i.serialize for i in bugs]])
    else:
        results['data'].append(["No Tests", "No Tests", "No Tests",
                                "No Tests", "No Tests", "No tests"])

    return jsonify(results)
