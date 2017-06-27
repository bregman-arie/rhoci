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
from flask import jsonify
from flask import Blueprint
from flask import render_template
import jenkins
import logging

import rhoci.models.agent as agent_model


logger = logging.getLogger(__name__)

job_analyzer = Blueprint('job_analyzer', __name__)


@job_analyzer.route('/job_analyzer', methods=['GET', 'POST'])
def index():
    """Job Analyzer page."""
    return render_template('job_analyzer.html')


@job_analyzer.route('/job_exists/', methods=['GET'])
@job_analyzer.route('/job_exists/<job_name>', methods=['GET'])
def job_exists(job_name=None):
    # all_args = request.args.lists()
    print job_name
    agent = agent_model.Agent.query.one()
    conn = jenkins.Jenkins(agent.url, agent.user, agent.password)
    job_exists = conn.job_exists("asasdsd")
    return jsonify(exists=job_exists)
