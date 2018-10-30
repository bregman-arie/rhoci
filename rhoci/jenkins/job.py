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
import json
import logging
import urllib2

import rhoci.jenkins.build as build_lib
from rhoci.db.base import db
import rhoci.models as models
import rhoci.rhosp.jenkins as rhosp_jenkins
import rhoci.rhosp.DFG as DFG_lib
from rhoci.rhosp import release
from rhoci.common.utils import convert_unixtime_to_datetime

LOG = logging.getLogger(__name__)


def insert_job_data_into_db(job):
    """Add job data into DB."""
    job_name = job['name']
    last_build_number = 'None'
    last_build_result = 'None'
    timestamp = None
    DFG = None
    squad = None

    if not models.Job.query.filter_by(name=job_name).count():
        # Get job type and release
        job_type = rhosp_jenkins.get_job_type(job_name.lower())
        if job_type.lower() == 'dfg':
            DFG = DFG_lib.get_DFG_name(job_name.lower())
            squad = DFG_lib.get_squad_name(job_name.lower())
        rel = rhosp_jenkins.get_job_release(job_name)

        # If there is build data, update DB accordingly
        if job.get('lastBuild'):
            build_lib.insert_build_data_into_db(job_name, job['lastBuild'])
            last_build_number = job['lastBuild'].get('number')
            last_build_result = job['lastBuild'].get('result')
            timestamp_unix = job['lastBuild'].get('timestamp')
            timestamp = convert_unixtime_to_datetime(timestamp_unix)

        # Create a Job DB object
        db_job = models.Job(name=job_name,
                            job_type=job_type,
                            release_number=int(rel),
                            last_build_number=last_build_number,
                            last_build_result=last_build_result,
                            DFG_name=DFG,
                            squad_name=squad,
                            timestamp=timestamp)

        # Add to DB and commit the change
        db.session.add(db_job)
        db.session.commit()


def job_exists(job):
    """Returns true if job exists"""
    agent = models.Agent.query.one()
    conn = rhosp_jenkins.Jenkins(agent.url, agent.user, agent.password)
    try:
        exists = conn.job_exists(job)
        message = "Couldn't find any job called %s " % job
    except rhosp_jenkins.JenkinsException:
        exists = False
        message = "Unable to reach Jenkins for some reason..."

    return exists, message


def add_new_job(name):
    """Add new job to DB."""
    job_type = rhosp_jenkins.get_job_type(name.lower())
    rel = release.extract_release(name)
    db_job = models.Job(name=name, job_type=job_type,
                        release_number=int(rel))
    db.session.add(db_job)
    db.session.commit()
    LOG.debug("Added job: %s to the DB" % name)


def add_bug(job, bug_num):
    """Adds a bug to."""
    job_db = models.Job.query.filter_by(name=job).first()
    bug_db = models.Bug.query.filter_by(number=bug_num).first()
    job_db.bugs.append(bug_db)
    db.session.commit()


def populate_db_with_jobs(agent):

    ALL_JOBS_API = ("/api/json/?tree=jobs"
                    "[name,lastBuild[result,number,timestamp]]")

    request = urllib2.Request(agent.url + ALL_JOBS_API)
    jobs_json = json.loads(
        urllib2.urlopen(request).read())

    for job in jobs_json['jobs']:
        if job['_class'] != 'com.cloudbees.hudson.plugins.folder.Folder':
            insert_job_data_into_db(job)


def construct_jobs_dictionary(jobs):
    """Returns structure that can be used by jquery datatable."""
    results = dict()
    results['data'] = list()
    for job in jobs:

        bug_assigned_to = 'No bugs'
        bug_status = 'No bugs'
        bug_number = 'No bugs'
        if job.bugs:
            bug_assigned_to = job.bugs[0].assigned_to
            bug_status = job.bugs[0].status
            bug_number = job.bugs[0].number

        if models.Build.query.filter_by(job=job.name,
                                        number=job.last_build_number).count():
            build_db = models.Build.query.filter_by(
                job=job.name,
                number=job.last_build_number).first()
            if build_db.failure_name:
                results['data'].append([job.name, build_db.failure_name,
                                        job.last_build_number, '',
                                        bug_assigned_to, bug_status, [
                                            i.serialize for i in job.bugs],
                                        bug_number])
            else:
                results['data'].append([job.name, job.last_build_result,
                                        job.last_build_number, '',
                                        bug_assigned_to, bug_status, [
                                            i.serialize for i in job.bugs],
                                        bug_number])
        else:
            results['data'].append([job.name, job.last_build_result,
                                    job.last_build_number, '',
                                    bug_assigned_to, bug_status, [
                                        i.serialize for i in job.bugs],
                                    bug_number])
    return results
