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

from rhoci.jenkins import api
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
        request = requests.get(self.url + api.CALLS['get_jobs'], verify=False)
        result_json = json.loads(request.text)
        return result_json['jobs']

    @staticmethod
    def add_job_to_db(job, properties):
        """Add job to the database."""
        print(job)
        job = api.adjust_job_data(job)
        new_job = Job(name=job['name'],
                      last_build=job['build'],
                      properties=properties)
        new_job.insert()

    @staticmethod
    def classify_and_insert_to_db(job):
        """Classifies job type and insert data based on classification
        to the db.
        """
        properties = {}
        properties['class'] = osp.get_job_class(job)
        if properties['class'] == 'DFG':
            properties['DFG'] = osp.get_DFG_name(job['name'])
            new_DFG = DFG_db(name=properties['DFG'])
            DFG_db.insert(new_DFG)
            properties['component'] = osp.get_component_name(job['name'])
            squad_name = DFG_db.get_squad(properties['DFG'],
                                          properties['component'])
            if squad_name:
                properties['squad'] = squad_name
        if properties['class'] != 'folder':
            release = osp.get_release(job['name'])
            properties['release'] = release
            JenkinsAgent.add_job_to_db(job, properties)

    def add_build_to_db(self, job_name, build):
        """Insets build into the database."""
        new_build = Build(
            job_name=job_name, number=build['number'],
            result=build['result'], timestamp=build['timestamp'])
        new_build.insert()
