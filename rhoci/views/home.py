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
import bugzilla
from flask import render_template
from flask import Blueprint
from flask import jsonify
from flask import request
import logging

import rhoci.agent.update as agent_update
from rhoci.jenkins import manager
import rhoci.models as models
from rhoci.views.doc import auto
import rhoci.rhosp.bug as rhosp_bug
import rhoci.jenkins.job as jenkins_job
import sys

if sys.version_info[0] >= 3:
    from xmlrpc.client import Fault
else:
    from xmlrpclib import Fault


LOG = logging.getLogger(__name__)

home = Blueprint('home', __name__)


@home.route('/')
def index():
    """Home page."""
    releases = models.Release.query.all()
    jobs = {}
    jobs['phase1'] = models.Job.query.filter_by(job_type='phase1')
    jobs['phase2'] = models.Job.query.filter_by(job_type='phase2')
    jobs['dfg'] = models.Job.query.filter_by(job_type='dfg')
    jobs_num = models.Job.query.count()
    nodes_num = models.Node.query.count()
    plugins_num = models.Plugin.query.count()

    return render_template('home.html',
                           releases=releases,
                           phase1=jobs['phase1'],
                           phase2=jobs['phase2'],
                           dfg=jobs['dfg'],
                           jobs_num=jobs_num,
                           nodes_num=nodes_num,
                           plugins_num=plugins_num)


@home.route('/releases/ajax/jobs/<job_type>_<release>')
def ajax_jobs(job_type, release):

    results = dict()
    results['data'] = list()

    jobs = models.Job.query.filter_by(
        job_type=job_type, release_number=int(release))

    for job in jobs:
        results['data'].append([job.name, job.last_build_status,
                                job.last_build_number])

    return jsonify(results)


@auto.doc(groups=['jobs', 'public'])
@home.route('/v2.0/jobs', methods=['GET', 'POST'])
def list_jobs():
    """Returns all jobs in the DB."""
    if request.method == 'POST':
        job = models.Job.query.filter_by(
            name=request.form['job_name']).first()
        jobs = job.serialize if job else {}
    else:
        jobs = [i.serialize for i in models.Job.query.all()]

    return jsonify(output=jobs)


@auto.doc(groups=['jobs', 'public'])
@home.route('/v2.0/jobs/<string:job_name>', methods=['GET', 'DELETE'])
def get_job(job_name):
    """Returns data on a specific job."""
    job = models.Job.query.filter_by(name=job_name).all()
    if job:
        if request.method == 'DELETE':
            agent_update.job_db_delete(job_name)
            return jsonify({'job name:': job_name,
                            'status': 'removed'})
        else:
            return jsonify(job[0].serialize)
    else:
        return jsonify({'exist': False})


@auto.doc(groups=['tests', 'public'])
@home.route('/v2.0/tests', methods=['GET', 'POST'])
def list_tests():
    """Returns all tests in the DB."""
    if request.method == 'POST':
        tests = models.TestBuild.query.filter_by(
            job_name=request.form['job_name'],
            build_number=request.form['build_number']).all()
    else:
        tests = [i.serialize for i in models.TestBuild.query.all()]

    return jsonify(tests=tests)


@auto.doc(groups=['update', 'public'])
@home.route('/v2.0/update_jobs', methods=['GET', 'POST'])
def update_jobs():
    """Shallow update of all jobs."""
    LOG.info("Jobs update requested.")
    agent_update.shallow_jobs_update()
    return jsonify({'status': 'OK'})


@home.route('/v2.0/jenkins_notifications', methods=['POST'])
def jenkins_notifications():
    """Recieving notifications from Jenkins."""
    LOG.info("Recieved notification from Jenkins.")
    LOG.debug("Data: %s" % request.data)
    status = manager.update_db(request.get_json(silent=True))
    return jsonify({'notification': status})


@auto.doc(groups=['builds', 'public'])
@home.route('/v2.0/builds', methods=['GET', 'POST'])
def builds():
    """Returns information on Jenkins builds."""
    builds = [i.serialize for i in models.Build.query.all()]
    return jsonify(builds=builds)


@auto.doc(groups=['rhosp', 'public'])
@home.route('/v2.0/dfg', methods=['GET', 'POST'])
def dfgs():
    """Returns all DFGs"""
    dfg = [i.serialize for i in models.DFG.query.all()]
    return jsonify(dfgs=dfg)


@auto.doc(groups=['failures', 'public'])
@home.route('/v2.0/failures', methods=['GET', 'POST'])
def failures():
    """Returns all failures"""
    failures = [i.serialize for i in models.Failure.query.all()]
    return jsonify(failures=failures)


@home.route('/releases', methods=['GET'])
def releases():

    agent = models.Agent.query.one()
    releases = models.Release.query.all()
    jobs = {}
    jobs['phase1'] = models.Job.query.filter_by(job_type='phase1')
    jobs['phase2'] = models.Job.query.filter_by(job_type='phase2')
    jobs['dfg'] = models.Job.query.filter_by(job_type='dfg')

    return render_template('releases.html',
                           releases=releases,
                           phase1=jobs['phase1'],
                           phase2=jobs['phase2'],
                           dfg=jobs['dfg'],
                           agent=agent)


@home.route('/bug_exists/')
def bug_exists():
    exists = True
    bug_num = request.args.get('bug_num')
    job_name = request.args.get('job_name')

    bzapi = bugzilla.Bugzilla("bugzilla.redhat.com")
    try:
        bug = bzapi.getbug(bug_num)
        if not models.Bug.query.filter_by(summary=bug.summary).count():
            rhosp_bug.add_bug(bug_num, bug.summary, bug.status,
                              system="bugzilla")
        jenkins_job.add_bug(job_name, bug_num)

    except Fault:
        LOG.warning("Couldn't find requested bug: %s" % str(bug_num))
        exists = False

    return jsonify(exists=exists)


@home.route('/bugs')
def bugs():
    """Bugs page."""
    bugs = models.Bug.query.all()
    agent = models.Agent.query.one()

    return render_template('bugs.html', bugs=bugs, agent=agent)


@home.route('/changelog')
def changelog():
    """Changelog page."""
    return render_template('changelog.html')


@home.route('/get_bugs_datatable/<job>', methods=['GET'])
@home.route('/get_bugs_datatable/', methods=['GET'])
def get_bugs_datatable(job=None):

    results = dict()
    results['data'] = list()
    if not job:
        job = request.args.get('job')

        job_db = models.Job.query.filter_by(name=job).first()
        for bug in job_db.bugs:
            results['data'].append([bug.summary, bug.number,
                                    bug.status, bug.system, ''])
        return jsonify(results)


@home.route('/remove_bug/', methods=['GET'])
@home.route('/remove_bug/<bug_num>_<job>_<test>_<remove_all>', methods=['GET'])
def remove_bug(bug_num=None, job=None, test=None, remove_all=None):
    """Removes bug from the database."""
    bug_num = request.args.get('bug_num')
    remove_all = request.args.get('remove_all')
    if remove_all:
        rhosp_bug.remove_from_all(bug_num)
    return jsonify(dict(status="OK"))
