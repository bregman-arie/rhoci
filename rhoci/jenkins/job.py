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
import logging

from rhoci.db.base import db
from rhoci.models import Agent
from rhoci.models import Job
from rhoci.rhosp import jenkins
from rhoci.rhosp import release

LOG = logging.getLogger(__name__)


def update_in_db(data):
    """Update job in DB."""
    job_name = data['name']

    if not Job.query.filter_by(name=job_name).count():
        # Get job type and release
        job_type = jenkins.get_job_type(job_name.lower())
        rel = jenkins.get_job_release(job_name)

        # Create Job DB object
        db_job = Job(name=job_name, job_type=job_type, release_number=int(rel))

        # Add to DB and commit the change
        db.session.add(db_job)
        db.session.commit()
        LOG.debug("Added job: %s to the DB" % (data['name']))


def job_exists(job):
    """Returns true if job exists"""
    agent = Agent.query.one()
    conn = jenkins.Jenkins(agent.url, agent.user, agent.password)
    try:
        exists = conn.job_exists(job)
        message = "Couldn't find any job called %s " % job
    except jenkins.JenkinsException:
        exists = False
        message = "Unable to reach Jenkins for some reason..."

    return exists, message


def add_new_job(name):
    """Add new job to DB."""
    job_type = jenkins.get_job_type(name.lower())
    rel = release.extract_release(name)
    db_job = Job(name=name, job_type=job_type,
                 release_number=int(rel))
    db.session.add(db_job)
    db.session.commit()
    LOG.debug("Added job: %s to the DB" % name)
