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
import jenkins
import logging
from multiprocessing import Process
import re
import time

from rhoci.agent import agent
import rhoci.lib.jenkins as jenkins_lib
import rhoci.models.job as job_model
import rhoci.models.agent as agent_model
import rhoci.models.node as node_model
from rhoci.db.base import db

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
        except Exception:
            self.active = False
        self.add_agent_to_db()

    def start(self):
        """Start running the jenkins agent."""
        while True:
            time.sleep(10)
            db.session.remove()

    def pre_start(self):
        """Populate the database with all the information from Jenkins."""
        with self.app.app_context():

            all_jobs = self.shallow_db_update()

            for job in all_jobs:
                # Now pull specific information for each job
                job_info = self.conn.get_job_info(job['name'])
                last_build_number = jenkins_lib.get_last_build_number(job_info)
                if last_build_number:
                    last_build_result = jenkins_lib.get_build_result(
                        self.conn, job['name'], last_build_number)
                else:
                    last_build_result = "None"

                # Update entry in database
                job_model.Job.query.filter_by(
                    name=job['name']).update(
                        dict(last_build_number=last_build_number,
                             last_build_result=last_build_result))
                db.session.commit()
                LOG.debug("Updated job from %s: %s" % (self.name, job['name']))

    def add_agent_to_db(self):
        """Adds the agent to the database."""
        with self.app.app_context():
            db_agent = agent_model.Agent(name=self.name)
            db.session.add(db_agent)
            db.session.commit()

    def update_number_of_jobs_plugins_nodes(self, jobs_num, nodes_num,
                                            plugins_num):
        """Updates the Jenkins agent db entry with number of jobs, nodes and

        plugins.
        """
        with self.app.app_context():
            agent_model.Agent.query.filter_by(name=self.name).update(
                dict(number_of_jobs=jobs_num,
                     number_of_nodes=nodes_num,
                     number_of_plugins=plugins_num,
                     active=self.active))
            LOG.debug("Updated number of jobs, nodes and plugins")
            db.session.commit()

    def get_job_type(self, name):
        """Returns job type based on its name."""
        if 'phase1' in name:
            return 'phase1'
        elif 'phase2' in name:
            return 'phase2'
        elif 'dfg' in name:
            return 'dfg'
        else:
            return 'other'

    def get_job_release(self, name):
        m = re.search('\d+', name)
        print m
        return m.group() if m else 0

    def shallow_db_update(self):
        """Insert jobs and nodes with only their names."""

        all_jobs = self.conn.get_all_jobs()
        all_nodes = self.conn.get_nodes()
        all_plugins = self.conn.get_plugins(depth=1)

        self.update_number_of_jobs_plugins_nodes(len(all_jobs), len(all_nodes),
                                                 len(all_plugins))

        for job in all_jobs:
            job_t = self.get_job_type(job['name'].lower())
            rel = self.get_job_release(job['name'])

            db_job = job_model.Job(name=job['name'],
                                   job_type=job_t,
                                   release_number=int(rel))
            db.session.add(db_job)
            db.session.commit()
            LOG.debug("Added job: %s to the DB" % (job['name']))

        for node in all_nodes:
            db_node = node_model.Node(name=node['name'])
            db.session.add(db_node)
            db.session.commit()
            LOG.debug("Added node: %s to the DB" % (node['name']))

        return all_jobs
