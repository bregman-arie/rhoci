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
import time
import sys

from rhoci.agent import agent
from rhoci.agent import update
import rhoci.jenkins.build as build_lib
import rhoci.jenkins.job as job_lib
import rhoci.jenkins.plugin as plugin_lib
import rhoci.jenkins.node as node_lib
import rhoci.models as models
from rhoci.db.base import db

LOG = logging.getLogger(__name__)


class Jenkins(agent.Agent):

    def __init__(self, user, password, url, app, name="jenkins"):

        super(Jenkins, self).__init__(name)
        self.user = user
        self.password = password
        self.url = url
        self.app = app
        self.pre_run_process = Process(target=self.pre_start)
        try:
            self.conn = jenkins.Jenkins(self.url, self.user, self.password)
            self.active = True
        except TypeError:
            LOG.error("Please specify jenkins address, user and token")
            sys.exit(2)
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

                # Populate db with different entities from Jenkins
                job_lib.populate_db_with_jobs(agent)
                plugin_lib.populate_db_with_plugins(agent)
                node_lib.populate_db_with_nodes(agent)

            # In case application was restarted or crushed, check if active
            # builds in DB are still active
            build_lib.check_active_builds(self.conn)

    def add_agent_to_db(self):
        """Adds the agent to the database."""
        with self.app.app_context():
            if not models.Agent.query.filter_by(name=self.name).count():
                db_agent = models.Agent(name=self.name,
                                        user=self.user,
                                        url=self.url,
                                        password=self.password)
                db.session.add(db_agent)
                db.session.commit()
