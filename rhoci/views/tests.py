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

from rhoci.models import Test
from rhoci.models import TestBuild


logger = logging.getLogger(__name__)

tests = Blueprint('tests', __name__)


@tests.route('/test_runs', methods=['GET'])
def test_runs():

    db_tests = TestBuild.query.all()
    all_tests = [test.serialize for test in db_tests]

    return render_template('tests.html', all_tests=all_tests)


@tests.route('/unique_tests', methods=['GET'])
def unique_tests():

    db_tests = Test.query.all()
    all_tests = [test.serialize for test in db_tests]

    return render_template('unique_tests.html', all_tests=all_tests)


@tests.route('/top_failing_tests', methods=['GET'])
def top_failing_tests():

    results = dict()
    results['data'] = list()

    db_tests = Test.query.limit(5).all()

    for test in db_tests:
        results['data'].append([test.class_name, test.failure, test.success])

    return jsonify(results)
