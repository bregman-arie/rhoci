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
from __future__ import absolute_import

import json
import logging
import requests

from rhoci.jenkins.api import API
from rhoci.models.job import Job
from rhoci.models.build import Build
from rhoci.models.DFG import DFG as DFG_db
from rhoci.jenkins import osp

LOG = logging.getLogger(__name__)


class JenkinsAgent():

    def __init__(self, user, password, url):

        self.user = user
        self.password = password
        self.url = url

    def run(self):
        """Runs the agent proess."""
        LOG.info("Running Jenkins agent")
        jobs = self.get_jobs()
        LOG.info("Obtained a list of jobs from Jenkins")
        for job in jobs:
            JenkinsAgent.classify_and_insert_to_db(job)
            if 'lastBuild' in job and job['lastBuild']:
                self.add_build_to_db(job['name'], job['lastBuild'])
        # Agent should run forever
        LOG.info("Running forever")
        while True:
            pass

    def get_jobs(self):
        """Returns jobs."""
        request = requests.get(self.url + API['get_jobs'], verify=False)
        result_json = json.loads(request.text)
        return result_json['jobs']

    @staticmethod
    def add_job_to_db(job, job_class, properties):
        """Add job to the database."""
        if 'lastBuild' in job:
            lb = job['lastBuild']
        else:
            lb = job['build']
        new_job = Job(_class=job_class, name=job['name'],
                      last_build=lb, properties=properties)
        new_job.insert()

    @staticmethod
    def classify_and_insert_to_db(job):
        """Classifies job type and insert data based on classification
        to the db.
        """
        properties = {}
        job_class = osp.get_job_class(job)
        if job_class == 'DFG':
            DFG_name = osp.get_DFG_name(job['name'])
            new_DFG = DFG_db(name=DFG_name)
            DFG_db.insert(new_DFG)
            comp_name = osp.get_component_name(job['name'])
            print(comp_name)
            squad_name = DFG_db.get_squad(DFG_name, comp_name)
            print(squad_name)
            properties = {'DFG': DFG_name, 'component': comp_name}
            if squad_name:
                properties['squad'] = squad_name
        if job_class != 'folder':
            JenkinsAgent.add_job_to_db(job, job_class, properties)

    def add_build_to_db(self, job_name, build):
        """Insets build into the database."""
        new_build = Build(
            job_name=job_name, number=build['number'],
            result=build['result'], timestamp=build['timestamp'])
        new_build.insert()
