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

from rhoci.models import Agent
from rhoci.models import Build


logger = logging.getLogger(__name__)

builds = Blueprint('builds', __name__)


@builds.route('/tests_compare')
def tests_compare():
    """Comparing tests of two different builds."""

    return render_template('tests_compare.html')


@builds.route('/job_exists/', methods=['GET'])
@builds.route('/job_exists/<job_name>', methods=['GET'])
def job_exists(job_name=None):

    return jsonify(exists=job_exists)


@builds.route('/active_builds', methods=['GET'])
def active():

    builds = Build.query.all()
    agent = Agent.query.one()

    return render_template('active_builds.html', agent=agent, builds=builds)
