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
from multiprocessing import Process
import re
import time

from rhoci.agent import agent
from rhoci.agent import update
import rhoci.jenkins.build as build_lib
import rhoci.jenkins.job as job_lib
import rhoci.models as models
from rhoci.db.base import db
from rhoci.rhosp.dfg import get_dfg_name

LOG = logging.getLogger(__name__)


class JenkinsAgent(agent.Agent):

    def __init__(self, name, user, password, url, app):

        super(JenkinsAgent, self).__init__(name)
        self.user = user
        self.password = password
        self.url = url
        self.app = app
        self.pre_run_process = Process(target=self.pre_start)
        try:
            self.conn = jenkins.Jenkins(self.url, self.user, self.password)
            self.active = True
        except Exception as e:
            LOG.info("Something went terribly wrong when " +
                     "starting Jenkins agent: %s" % e.message)
            self.active = False
        self.add_agent_to_db()

    def start(self):
        """Start running the Jenkins agent."""
        while True:
            time.sleep(self.app.config['RHOCI_UPDATE_INTERVAL'])
            LOG.info("Updating jobs")
            with self.app.app_context():
                update.shallow_jobs_update()
            LOG.info("Update complete")

    def pre_start(self):
        """Populate the database with information from Jenkins

        Jobs - name, last build status, last build_number
        Builds - Job name, Status, Number
        """
        with self.app.app_context():

            # If there is no update time, it means the application never
            # contacted Jenkins so run update without additional
            # If there was an update, check if one hour passed since
            # last update
            agent = models.Agent.query.filter_by(name=self.name).first()
            if not agent.update_time or (agent.update_time -
                                         datetime.datetime.utcnow() >
                                         datetime.timedelta(minutes=59)):

                # Update timestamp for last Jenkins update
                models.Agent.query.filter_by(
                    name=self.name).update(dict(
                        update_time=datetime.datetime.utcnow()))
                LOG.debug("Updated agent timestamp")

                # Populate db with jobs
                job_lib.populate_db_with_jobs(agent)

            # In case application was restarted or crushed, check if active
            # builds in DB are still active
            build_lib.check_active_builds(self.conn)

    def remove_jobs_from_db(self, jobs):
        """Removes jobs from DB that no longer exist on Jenkins."""
        with self.app.app_context():
            for job in jobs:
                if not models.Job.query.filter_by(name=job):
                    LOG.debug("Removing job: %s from DB" % job)

    def update_job_in_db(self, job):
        last_build_result = "None"
        with self.app.app_context():
            try:
                job_info = self.conn.get_job_info(job['name'])
                last_build_number = build_lib.get_last_build_number(
                    job_info)
            except Exception as e:
                LOG.info("Unable to fetch information for %s: %s" % (
                    job['name'], e.message))
            if last_build_number:
                last_build_result = build_lib.get_build_status(
                    self.conn, job['name'], last_build_number)
                db_build = models.Build(job=job['name'],
                                        number=last_build_number,
                                        status=last_build_result)
                db.session.add(db_build)
                db.session.commit()

            # Update entry in database
            models.Job.query.filter_by(
                name=job['name']).update(
                    dict(last_build_number=last_build_number,
                         last_build_result=last_build_result))
            db.session.commit()
            LOG.debug("Updated job from %s: %s" % (self.name, job['name']))

    def add_agent_to_db(self):
        """Adds the agent to the database."""
        with self.app.app_context():
            if not models.Agent.query.filter_by(name=self.name).count():
                db_agent = models.Agent(name=self.name,
                                        url=self.url,
                                        password=self.password)
                db.session.add(db_agent)
                db.session.commit()

    def get_job_type(self, name):
        """Returns job type based on its name."""
        if 'phase1' in name:
            return 'phase1'
        elif 'phase2' in name:
            return 'phase2'
        elif 'dfg' in name:
            dfg = get_dfg_name(name)
            if (not models.DFG.query.filter_by(name=dfg).count() and
                    dfg.lower() != 'dfg'):
                db_dfg = models.DFG(name=dfg)
                db.session.add(db_dfg)
                db.session.commit()
            return 'dfg'
        else:
            return 'other'

    def get_job_release(self, name):
        m = re.search('-\d{1,2}', name)
        return m.group().split('-')[1] if m else 0
