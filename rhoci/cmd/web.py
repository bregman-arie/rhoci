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
import rhoci.parser.web as web_parser
import rhoci.web


def create_parser():
    """Returns parsed arguments from parser."""
    parser = web_parser.create()
    return parser.parse_args()


def launch_app(args=None):
    """Runs Web application."""
    web_server = rhoci.web.WebApp(args)
    web_server.run()


def main():
    """Main entry for running the web server."""

    args = create_parser()
    launch_app(args)
