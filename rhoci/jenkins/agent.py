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
import time

from rhoci.jenkins import api
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
        LOG.info("Starting rhoci agent")
        jobs = self.get_jobs()
        self.remove_jobs([job['name'] for job in jobs])
        LOG.info("Obtained a list of jobs from Jenkins. Processing...")
        for job in jobs:
            JenkinsAgent.classify_and_insert_to_db(job)
        # Agent should run forever
        LOG.info("Prcoessing complete. Switching to standby mode.")
        while True:
            self.wait_to_next_midnight()
            jobs = self.get_jobs()
            self.remove_jobs([job['name'] for job in jobs])

    def remove_jobs(self, jenkins_jobs):
        """Removes jobs from the database based on the list of jobs
        in Jenkins.
        """
        for job in Job.find():
            if job['name'] not in jenkins_jobs:
                Job.delete_one(job['name'])
                LOG.info("Deleted job: %s" % job['name'])

    @staticmethod
    def wait_to_next_midnight():
        """Wait to tomorrow 00:00 am."""
        time_now = time.localtime()
        time_now = time.mktime(time_now[:3] + (0, 0, 0) + time_now[6:])
        time.sleep(time_now + 24 * 3600 - time.time())

    def get_jobs(self):
        """Returns jobs."""
        request = requests.get(self.url + api.API_CALLS['get_jobs'],
                               verify=False)
        result_json = json.loads(request.text)
        return result_json['jobs']

    def get_tests(self, job, build):
        """Returns tests given a job name and a build number."""
        request = requests.get(
            self.url + api.API_CALLS['get_tests'].format(job, build),
            verify=False)
        result_json = json.loads(request.text)
        print(result_json)
        return result_json['tests']

    @staticmethod
    def add_job_to_db(job, properties):
        """Add job to the database."""
        job = api.adjust_job_data(job)
        new_job = Job(name=job['name'],
                      last_build=job['build'],
                      **properties)
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
            properties['component'] = osp.get_component_name(
                job['name'], properties['DFG'])
            properties['squad'] = DFG_db.get_squad(properties['DFG'],
                                                   properties['component'])
        if properties['class'] != 'folder':
            release = osp.get_release(job['name'])
            properties['release'] = release
            JenkinsAgent.add_job_to_db(job, properties)
