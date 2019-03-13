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
        print(jobs)
        for job in jobs:
            self.add_job_to_db(job)
        while True:
            pass

    def get_jobs(self):
        """Returns jobs."""
        request = requests.get(self.url + API['get_jobs'], verify=False)
        result_json = json.loads(request.text)
        return result_json['jobs']

    def add_job_to_db(self, job):
        """Add job to the database."""
        # Avoid inserting folders to the database
        if job['_class'] != 'com.cloudbees.hudson.plugins.folder.Folder':
            new_job = Job(_class=job['_class'], name=job['name'],
                          last_build=job['lastBuild'])
            new_job.save_to_db()

    def insert_DFG_data_to_db(self, DFGs):
        """Iterates over a list of DFGs and inserts their data into the db."""
        for DFG in DFGs:
            new_DFG = DFG_db(
                name=DFG['name'],
                squads=[{'name': sqd['name'],
                         'components': sqd[
                             'components']} for sqd in DFG['squads']])
            new_DFG.save_to_db()
