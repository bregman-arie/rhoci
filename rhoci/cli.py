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
import argparse

import rhoci.web

APP_NAME = "RHOCI"
CONF_FILE = "/etc/{0}/{0}.conf".format(APP_NAME.lower())


def create_parser():
    """Returns argparse parser."""

    parser = argparse.ArgumentParser()

    parser.add_argument('--conf', '-c', dest="config_file",
                        default=CONF_FILE,
                        help='Configuration file')
    parser.add_argument('--port', '-p', dest="%s_SERVER_PORT" % APP_NAME,
                        help='Server port')
    parser.add_argument('--demo', dest="demo", help='Run in demo mode',
                        action='store_true')
    parser.add_argument('--debug', dest="debug", help='Turn on debug',
                        action='store_true')

    return parser


def launch_app(args=None):
    """Runs Web application."""
    web_server = rhoci.web.Server(args)
    web_server.run()


def main():
    """Main entry for running the web server."""
    parser = create_parser()
    args = parser.parse_args()
    launch_app(args)
