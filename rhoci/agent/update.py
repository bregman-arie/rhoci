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

import rhoci.jenkins.server as jenkins_server
import rhoci.rhosp.jenkins as rhosp_jenkins
import rhoci.rhosp.dfg as rhosp_dfg

LOG = logging.getLogger(__name__)


def shallow_jobs_update():
    """Perform shallow (level 0) update of all the jobs."""
    # Get connection to Jenkins
    agent = models.Agent.query.all()[0]
    conn = jenkins_server.get_connection(agent.url, agent.user, agent.password)

    # Get a list of all jobs from Jenkins
    try:
        all_jobs = conn.get_all_jobs()

        # Check if some jobs no longer exist
        deleted_jobs = set(
            [x.name for x in models.Job.query.all()]).difference(
                set([x['name'] for x in all_jobs]))
        if deleted_jobs:
            LOG.info(
                "Found jobs in DB that no longer exist: %s" % deleted_jobs)
            for job in deleted_jobs:
                job_db_delete(job)

        agent.update_time = datetime.datetime.utcnow()
        db.session.commit()
    except jenkins.JenkinsException:
        LOG.warning("Could not update. I'll try again next time")


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
            name=test.name, class_name=test.class_name).count()
        if (unique_test.failure == 1 and unique_test.success == 0) or (
                unique_test.failure == 0 and unique_test.success == 1):
            db.session.delete(unique_test)
        elif test.status == 'PASSED':
            models.Test.query.filter_by(class_name=test.class_name,
                                        name=test.name).update(
                                            {'success': models.Test.success -
                                             1})
        else:
            models.Test.query.filter_by(class_name=test.class_name,
                                        name=test.name).update(
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


def build_db_update(build_data):
    """Update DB with given build data."""
    if db.session.query(
        models.Build).filter_by(job=build_data['name'],
                                number=build_data['build']['number']).scalar():
        LOG.debug("Build exists. Updating its records.")
    else:
        pass
