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
import datetime
import jenkins
import logging
from concurrent.futures import ThreadPoolExecutor

from rhoci.db.base import db
import rhoci.jenkins.build as jenkins_lib
import rhoci.jenkins.server as jenkins_server
import rhoci.models as models
import rhoci.rhosp.jenkins as rhosp_jenkins
import rhoci.rhosp.dfg as rhosp_dfg

LOG = logging.getLogger(__name__)


def shallow_jobs_update():
    """Perform shallow (level 0) update of all the jobs."""
    # Get connection to Jenkins
    agent = models.Agent.query.all()[0]
    conn = jenkins_server.get_connection(agent.url, agent.user, agent.password)

    # Get a list of all jobs from Jenkins
    all_jobs = conn.get_all_jobs()

    # Update every found job
    with ThreadPoolExecutor(100) as executor:
        for job in all_jobs:
            executor.submit(job_db_update, job, conn)

    # Check if some jobs no longer exist
    deleted_jobs = set([x.name for x in models.Job.query.all()]).difference(
        set([x['name'] for x in all_jobs]))
    if deleted_jobs:
        LOG.info("Found jobs in DB that no longer exist: %s" % deleted_jobs)
        for job in deleted_jobs:
            job_db_delete(job)

    agent.update_time = datetime.datetime.utcnow()
    db.session.commit()


def job_db_delete(job):
    """Delete job entry from DB."""
    db_job = models.Job.query.filter_by(name=job).first()
    db.session.delete(db_job)
    db.session.commit()
    LOG.info("Removed job %s from the DB" % job)
    models.Build.query.filter_by(job=job).delete()
    tests_build = models.TestBuild.query.filter_by(job=job).all()
    for test in tests_build:
        unique_test = models.Test.query.filter_by(
            name=test.test_name, class_name=test.class_name).count()
        if (unique_test.failure == 1 and unique_test.success == 0) or (
                unique_test.failure == 0 and unique_test.success == 1):
            db.session.delete(unique_test)
        elif test.status == 'PASSED':
            models.Test.query.filter_by(class_name=test.class_name,
                                        name=test.test_name).update(
                                            {'success': models.Test.success -
                                             1})
        else:
            models.Test.query.filter_by(class_name=test.class_name,
                                        name=test.test_name).update(
                                            {'failure': models.Test.failure -
                                             1})
        db.session.commit()
    models.TestBuild.query.filter_by(job=job).delete()
    db.session.commit()

    if rhosp_jenkins.get_job_type(job) == 'dfg':
        dfg = rhosp_dfg.get_dfg_name(job)
        if models.Job.query.filter(models.Job.name.contains(
                'DFG-%s' % dfg)).count() == 1:
            models.dfg.filter_by(name=dfg).delete()
            db.session.commit()


def job_db_update(job, conn):
    """Update a given job row in the DB."""

    try:
        job_info = conn.get_job_info(job['name'])
        last_build_number = jenkins_lib.get_last_build_number(job_info)

    except Exception as e:
        LOG.info("Unable to fetch information for %s: %s" % (job['name'],
                                                             e.message))
        if isinstance(e, jenkins.NotFoundException):
            LOG.info("Removing job %s since it no longer exist on Jenkins" %
                     job['name'])
            job_db = models.Job.query.filter_by(name=job['name']).first()
            db.session.delete(job_db)
            db.session.commit()

    if last_build_number:
        last_build_status = jenkins_lib.get_build_status(
            conn, job['name'], last_build_number)
    else:
        last_build_status = "None"

    # Update entry in database
    models.Job.query.filter_by(
        name=job['name']).update(
            dict(last_build_number=last_build_number,
                 last_build_status=last_build_status))


def build_db_update(build_data):
    """Update DB with given build data."""
    if db.session.query(
        models.Build).filter_by(job=build_data['name'],
                                number=build_data['build']['number']).scalar():
        LOG.debug("Build exists. Updating its records.")
    else:
        pass
