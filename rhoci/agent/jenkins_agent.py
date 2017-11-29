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
from concurrent.futures import ThreadPoolExecutor
import re
import sys
import time

from rhoci.agent import agent
from rhoci.agent import update
import rhoci.jenkins.build as build_lib
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
            LOG.info("Something went terribly wrong starting Jenkins agent: %s"
                     % e.message)
            self.active = False
        self.add_agent_to_db()

    def start(self):
        """Start running the jenkins agent."""
        while True:
            time.sleep(3600)
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

                # Do a shallow update (detailed description in docstring)
                all_jobs = self.shallow_db_update()

                # Update information regarding the job in the DB
                with ThreadPoolExecutor(100) as executor:
                    for job in all_jobs:
                        executor.submit(self.update_job_in_db, job)

            # In case application was restarted or crushed, check if active
            # builds in DB are still active
            build_lib.check_active_builds(self.conn)

            # Analyze failed builds
            failed_builds = models.Build.query.filter_by(
                status='FAILURE').all()
            for build_db in failed_builds:
                if not build_db.failure_name:
                    LOG.info("Analyzing job %s build %s" % (build_db.job,
                                                            build_db.number))
                    build_lib.analyze_failure(build_db.job, build_db.number)

    def remove_jobs_from_db(self, jobs):
        """Removes jobs from DB that no longer exist on Jenkins."""
        with self.app.app_context():
            for job in jobs:
                if not models.Job.query.filter_by(name=job):
                    LOG.debug("Removing job: %s from DB" % job)

    def update_job_in_db(self, job):
        last_build_status = "None"
        with self.app.app_context():
            try:
                job_info = self.conn.get_job_info(job['name'])
                last_build_number = build_lib.get_last_build_number(
                    job_info)
            except Exception as e:
                LOG.info("Unable to fetch information for %s: %s" % (
                    job['name'], e.message))
            if last_build_number:
                last_build_status = build_lib.get_build_status(
                    self.conn, job['name'], last_build_number)
                db_build = models.Build(job=job['name'],
                                        number=last_build_number,
                                        status=last_build_status)
                db.session.add(db_build)
                db.session.commit()

            # Update entry in database
            models.Job.query.filter_by(
                name=job['name']).update(
                    dict(last_build_number=last_build_number,
                         last_build_status=last_build_status))
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

    def shallow_db_update(self):
        """Insert jobs, nodes and plugins to DB (names only)."""

        try:
            all_jobs = self.conn.get_all_jobs()
            all_nodes = self.conn.get_nodes()
            all_plugins = self.conn.get_plugins()
        except Exception as e:
            LOG.error("Failed to retrieve data from Jenkins: %s", e)
            self.active = False
            sys.exit(2)

        for job in all_jobs:
            if not models.Job.query.filter_by(name=job['name']).count():
                job_t = self.get_job_type(job['name'].lower())
                rel = self.get_job_release(job['name'])
                db_job = models.Job(name=job['name'],
                                    job_type=job_t,
                                    release_number=int(rel))
                db.session.add(db_job)
                db.session.commit()
                LOG.debug("Added job: %s to the DB" % (job['name']))

        for node in all_nodes:
            if not models.Node.query.filter_by(name=node['name']).count():
                db_node = models.Node(name=node['name'])
                db.session.add(db_node)
                db.session.commit()
                LOG.debug("Added node: %s to the DB" % (node['name']))

        for plugin in all_plugins.iteritems():
            plugin_name = plugin[1]['longName']
            if not models.Plugin.query.filter_by(
                    name=plugin_name).count():
                db_plugin = models.Plugin(name=plugin_name)
                db.session.add(db_plugin)
                db.session.commit()
                LOG.debug("Added plugin: %s to the DB" % (plugin_name))

        return all_jobs
