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
        self.get_jobs_and_insert_data_to_db()
        # Agent should run forever
        LOG.info("Running forever")
        while True:
            pass

    def get_jobs(self):
        """Returns jobs."""
        request = requests.get(self.url + API['get_jobs'], verify=False)
        result_json = json.loads(request.text)
        return result_json['jobs']

    def get_jobs_and_insert_data_to_db(self):
        """Get jobs from Jenkins and insert data to DB based on job class."""
        jobs = self.get_jobs()
        LOG.info("Obtained list of jobs")

        # Add jobs (and any related info extracted) to the DB
        for job in jobs:
            job_class = osp.get_job_class(job)
            if job_class != 'folder':
                self.add_job_to_db(job, job_class)
            if job_class == 'DFG':
                DFG_name = osp.get_DFG_name(job['name'])
                DFG_db.insert(DFG_db(name=DFG_name))
            if job['last_build']:
                self.add_build_to_db(job['name'], job['last_build'])

    def add_build_to_db(self, job_name, build):
        """Insets build into the database."""
        print(job_name)
        print(build)

    def add_job_to_db(self, job, job_class):
        """Add job to the database."""
        new_job = Job(_class=job_class, name=job['name'],
                      last_build=job['lastBuild'])
        new_job.insert()
