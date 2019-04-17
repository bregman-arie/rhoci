# Copyright 2019 Arie Bregman
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
from rhoci.common.utils import unixtime_to_datetime

CALLS = {'get_jobs':
         "/api/json/?tree=jobs[name,lastBuild[result,number,timestamp]]"}


def adjust_job_data(job):
    """Adjusts job data to unified structure supported by the app."""
    if 'lastBuild' in job:
        job['build'] = job.pop('lastBuild')
    if job['build']:
        if 'result' in job['build']:
            job['build']['status'] = job['build'].pop('result')
        job['build']['timestamp'] = unixtime_to_datetime(
            job['build']['timestamp'])
    return job


def adjust_build_data(build):
    """Adjusts build data to unified structure supported by the app."""
    if 'timestamp' in build:
        build['timestamp'] = unixtime_to_datetime(build['timestamp'])
    return build
