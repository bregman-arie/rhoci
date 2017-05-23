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


def create_runserver_subparser(subparsers, parent_parser):
    """Adds runserver sub-parser"""

    runserver_parser = subparsers.add_parser(
        "run", parents=[parent_parser])

    runserver_parser.add_argument(
        '--conf', '-c', dest="config_file", help='RHOCI configuration file')


def create():
    """Returns argparse parser."""

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--debug', required=False, action='store_true',
                               dest="debug", help='Turn DEBUG on')

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="parser")

    create_runserver_subparser(subparsers, parent_parser)

    return parser
