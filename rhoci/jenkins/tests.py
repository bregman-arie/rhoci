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
from __future__ import absolute_import

import logging

from rhoci.common.config import Config
from rhoci.jenkins.agent import JenkinsAgent

LOG = logging.getLogger(__name__)


def get_tests(job, build):
    """returns tests given a job name and build number."""
    app_conf = Config()
    jenkins_agent = JenkinsAgent(app_conf.config['jenkins']['user'],
                                 app_conf.config['jenkins']['password'],
                                 app_conf.config['jenkins']['url'])
    tests = jenkins_agent.get_tests(job, build)
    return tests
