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

import rhoci.models.agent as agent_model
from rhoci.views.doc import auto
import rhoci.models.release as release_model
import rhoci.models.job as job_model

logger = logging.getLogger(__name__)

home = Blueprint('home', __name__)


@home.route('/')
def index():
    """Home page."""
    releases = release_model.Release.query.all()
    jobs = {}
    jobs['phase1'] = job_model.Job.query.filter_by(job_type='phase1')
    jobs['phase2'] = job_model.Job.query.filter_by(job_type='phase2')
    jobs['dfg'] = job_model.Job.query.filter_by(job_type='dfg')
    agent = agent_model.Agent.query.one()

    return render_template('home.html',
                           releases=releases,
                           agent=agent,
                           phase1=jobs['phase1'],
                           phase2=jobs['phase2'],
                           dfg=jobs['dfg'])


@home.route('/releases/ajax/jobs/<job_type>_<release>')
def ajax_jobs(job_type, release):

    results = dict()
    results['data'] = list()

    jobs = job_model.Job.query.filter_by(job_type=job_type,
                                         release_number=int(release))

    for job in jobs:
        results['data'].append([job.name, job.last_build_result,
                                job.last_build_number])

    return jsonify(results)


@auto.doc(groups=['jobs', 'public'])
@home.route('/v2.0/jobs', methods=['GET'])
def list_jobs():
    """Returns all jobs in the DB."""
    jobs = [i.serialize for i in job_model.Job.query.all()]

    return jsonify(jobs)


@auto.doc(groups=['jobs', 'public'])
@home.route('/v2.0/jobs/<string:job_name>', methods=['GET'])
def get_job(job_name):
    """Returns data on a specific job."""
    job = job_model.Job.query.filter_by(name=job_name).all()
    if job:
        return jsonify(job[0].serialize)
    else:
        return jsonify({'exist': False})
