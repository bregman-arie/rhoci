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

import argparse
import logging

from rhoci.jenkins.agent import JenkinsAgent
from rhoci.common.config import Config

LOG = logging.getLogger(__name__)


def create_parser():
    """Returns argparse parser."""

    parser = argparse.ArgumentParser()

    parser.add_argument('--conf', '-c', dest="config_file",
                        help='Configuration file')
    parser.add_argument('--debug', dest="debug", help='Turn on debug',
                        action='store_true')
    return parser


def setup_logging(debug):
    """Sets the logging."""
    format = '%(message)s'
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format=format)


def run_agent(args=None):
    """Creates and runs the agent."""
    setup_logging(args.debug)
    app_conf = Config()
    jenkins_agent = JenkinsAgent(app_conf.config['jenkins']['user'],
                                 app_conf.config['jenkins']['password'],
                                 app_conf.config['jenkins']['url'])
    jenkins_agent.run()


def main():
    """Main entry for running the web server."""
    parser = create_parser()
    args = parser.parse_args()
    run_agent(args)
