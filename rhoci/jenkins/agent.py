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
import time

LOG = logging.getLogger(__name__)


class JenkinsAgent():

    def __init__(self, user, password, url):

        self.user = user
        self.password = password
        self.url = url

    def run(self):
        """Runs the agent proess."""
        LOG.info("Running Jenkins agent")
        while True:
            pass

    def start(self):
        """Start running the Jenkins agent."""
        while True:
            time.sleep(self.app.config['RHOCI_UPDATE_INTERVAL'])
            LOG.info("Updating jobs")
            # with self.app.app_context():
            # update.shallow_jobs_update()
            # LOG.info("Update complete")

    def pre_start(self):
        """Populate the database with information from Jenkins"""
        with self.app.app_context():
            pass

            # If there is no update time, it means the application never
            # contacted Jenkins so run update immediately
            # If there was an update, check if one hour passed since
            # last update
            # agent = models.Agent.query.filter_by(name=self.name).first()
            # if not agent.update_time or (agent.update_time -
            #                             datetime.datetime.utcnow() >
            #                             datetime.timedelta(minutes=59)):

            # Populate db with different entities from Jenkins
            #    job_lib.populate_db_with_jobs(agent)
            #    plugin_lib.populate_db_with_plugins(agent)
            #    node_lib.populate_db_with_nodes(agent)

            # Update timestamp for last Jenkins update
            #    models.Agent.query.filter_by(
            #        name=self.name).update(dict(
            #            update_time=datetime.datetime.utcnow()))
            #    LOG.debug("Updated agent timestamp")

            # else:
            #    LOG.debug("Last update was less than one hour." +
            #              " Skipping Jenkins agent update.")
            # In case application was restarted or crushed, check if active
            # builds in DB are still active
            # build_lib.check_active_builds(self.conn)
