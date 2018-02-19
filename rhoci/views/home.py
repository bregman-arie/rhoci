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
import sys

import rhoci.agent.update as agent_update
from rhoci.jenkins import manager
from rhoci.views.doc import auto
import rhoci.rhosp.bug as rhosp_bug
import rhoci.jenkins.job as jenkins_job
import rhoci.jenkins.test as jenkins_test
import rhoci.rhosp.release as release

if sys.version_info[0] >= 3:
    from xmlrpc.client import Fault
else:
    from xmlrpclib import Fault


LOG = logging.getLogger(__name__)

home = Blueprint('home', __name__)


def dfg_summary(dfg):
    """Returns a dictionary which represents the summary of a given DFG."""
    import pdb
    pdb.set_trace()
    return {'FAILURE': models.Job.query.filter(models.Job.name.contains(
        'DFG-%s' % dfg), models.Job.builds.status.like('FAILURE')).count(),
        'SUCCESS': models.Job.query.filter(
            models.Job.name.contains(
                'DFG-%s' % dfg), models.Job.last_build_result.like(
                'SUCCESS')).count(), 'UNSTABLE': models.Job.query.filter(
                    models.Job.name.contains('DFG-%s' % dfg),
                    models.Job.last_build_result.like(
                        'UNSTABLE')).count(),
        'None': models.Job.query.filter(models.Job.name.contains(
            'DFG-%s' % dfg), models.Job.last_build_result.is_('None')).count(),
        'ABORTED': models.Job.query.filter(models.Job.name.contains(
            'DFG-%s' % dfg), models.Job.last_build_result.is_(
                'ABORTED')).count(),
        'count': models.Job.query.filter(
            models.Job.name.contains('DFG-%s' % dfg)).count()}


def get_percentage(num1, num2):
    """Returns the percentage of two given numbers."""
    if num1 and num2:
        return int(100 * (float(num1) / float(num2)))
    else:
        return 0


@home.route('/')
def index():
    """Home page."""
    releases = models.Release.query.all()
    jobs = {}
    jobs['phase1'] = models.Job.query.filter_by(job_type='phase1')
    jobs['phase2'] = models.Job.query.filter_by(job_type='phase2')
    jobs['dfg'] = models.Job.query.filter_by(job_type='dfg')
    jobs_num = models.Job.query.count()
    builds_num = models.Build.query.count()
    tests_num = models.Test.query.count()
    bugs_num = models.Bug.query.count()
    nodes_num = models.Node.query.count()
    plugins_num = models.Plugin.query.count()
    agent = models.Agent.query.one()

    storage = dfg_summary('storage')
    network = dfg_summary('network')
    compute = dfg_summary('compute')

    last_rel_num = release.get_last_release()
    last_release = {'number': last_rel_num,
                    'total_jobs': models.Job.query.filter_by(
                        release_number=last_rel_num).count(),
                    'failed_jobs': models.Job.query.filter_by(
                        release_number=last_rel_num,
                        last_build_result='FAILURE').count(),
                    'passed_jobs': models.Job.query.filter_by(
                        release_number=last_rel_num,
                        last_build_result='SUCCESS').count(),
                    'unstable_jobs': models.Job.query.filter_by(
                        release_number=last_rel_num,
                        last_build_result='UNSTABLE').count(),
                    'never_executed_jobs': models.Job.query.filter_by(
                        release_number=last_rel_num,
                        last_build_result='None').count()}

    last_release['failed_percent'] = get_percentage(
        last_release['failed_jobs'], last_release['total_jobs'])
    last_release['passed_percent'] = get_percentage(
        last_release['passed_jobs'], last_release['total_jobs'])
    last_release['unstable_percent'] = get_percentage(
        last_release['unstable_jobs'], last_release['total_jobs'])
    last_release['never_executed_percent'] = get_percentage(
        last_release['never_executed_jobs'], last_release['total_jobs'])

    return render_template('home.html',
                           releases=releases, phase1=jobs['phase1'],
                           phase2=jobs['phase2'], dfg=jobs['dfg'],
                           jobs_num=jobs_num, nodes_num=nodes_num,
                           plugins_num=plugins_num, builds_num=builds_num,
                           tests_num=tests_num, bugs_num=bugs_num,
                           network=network, compute=compute, storage=storage,
                           last_release=last_release, agent=agent)


@home.route('/releases/ajax/jobs/<job_type>_<release>')
def ajax_jobs(job_type, release):

    results = dict()
    results['data'] = list()

    jobs = models.Job.query.filter_by(
        job_type=job_type, release_number=int(release))

    for job in jobs:
        results['data'].append([job.name, job.last_build_result,
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
    """Returns all unique tests in the DB."""
    tests = [i.serialize for i in models.Test.query.all()]

    return jsonify(tests=tests)


@auto.doc(groups=['release', 'public'])
@home.route('/v2.0/releases', methods=['GET'])
def list_releases():
    """Returns all the releases in the DB."""
    releases = [i.serialize for i in models.Release.query.all()]

    return jsonify(releases=releases)


@auto.doc(groups=['bugs', 'public'])
@home.route('/v2.0/bugs', methods=['GET'])
def list_bugs():
    """Returns all the bugs in the DB."""
    bugs = [i.serialize for i in models.Bug.query.all()]

    return jsonify(bugs=bugs)


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
    err_msg = ""
    bug_num = request.args.get('bug_num')
    job_name = request.args.get('job_name')
    test_name = request.args.get('test_name')
    class_name = request.args.get('test_class')
    apply_on_class = request.args.get('apply_on_class')

    bzapi = bugzilla.Bugzilla("bugzilla.redhat.com")
    try:
        bug = bzapi.getbug(bug_num)
        if bug.is_open:
            if not models.Bug.query.filter_by(summary=bug.summary).count():
                rhosp_bug.add_bug(bug_num, bug.summary, bug.status,
                                  bug.assigned_to, system="bugzilla")
            if job_name:
                jenkins_job.add_bug(job_name, bug_num)
            else:
                jenkins_test.add_bug(class_name, test_name, bug_num,
                                     apply_on_class)
        else:
            exists = False
            err_msg = "You are trying to add closed bug. Outrageous."

    except Fault:
        LOG.warning("Couldn't find requested bug: %s" % str(bug_num))
        err_msg = "Couldn't find a bug using the given bug number."
        exists = False

    except OverflowError:
        LOG.warning("User provided bug number that is too big")
        err_msg = ("...and server crashed again. Not sure why people provide "
                   "these long numbers.")
        exists = False

    return jsonify(exists=exists, err_msg=err_msg)


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
@home.route('/get_bugs_datatable/<job>_<test_class>_<test_name>',
            methods=['GET'])
@home.route('/get_bugs_datatable/', methods=['GET'])
def get_bugs_datatable(job=None, test_class=None, test_name=None):

    results = dict()
    results['data'] = list()
    if not job:
        job = request.args.get('job')
    if not test_class:
        test_class = request.args.get('test_class')
        test_name = request.args.get('test_name')

    if job:
        job_db = models.Job.query.filter_by(name=job).first()
        bugs = job_db.bugs
    else:
        test_db = models.Test.query.filter_by(class_name=test_class,
                                              test_name=test_name).first()
        bugs = test_db.bugs

    for bug in bugs:
        results['data'].append([bug.summary, bug.number, bug.assigned_to,
                                bug.status, bug.system, ''])
    return jsonify(results)


@home.route('/remove_bug/', methods=['GET'])
@home.route('/remove_bug/<bug_num>_<job>_<remove_all>', methods=['GET'])
def remove_bug(bug_num=None, job=None, remove_all=None):
    """Removes bug from the database."""
    bug_num = request.args.get('bug_num')
    job = request.args.get('job')
    remove_all = request.args.get('remove_all')
    if remove_all == "true":
        rhosp_bug.remove_from_all(bug_num)
    else:
        rhosp_bug.remove_from_job(bug_num, job)
    return jsonify(dict(status="OK"))


@home.route('/remove_tests_bug/', methods=['GET'])
@home.route(
    '/remove_tests_bug/<bug_num>_<test_name>_<test_class>_<remove_all>',
    methods=['GET'])
def remove_tests_bug(bug_num=None, test_name=None, test_class=None,
                     remove_all=None):
    """Unlink bug from a given test or a test class."""
    bug_num = request.args.get('bug_num')
    test_name = request.args.get('test_name')
    test_class = request.args.get('test_class')
    remove_all = request.args.get('remove_all')

    if remove_all == "true":
        rhosp_bug.remove_from_all(bug_num)
    else:
        rhosp_bug.remove_from_test(bug_num, test_class, test_name)

    return jsonify(dict(status="OK"))
