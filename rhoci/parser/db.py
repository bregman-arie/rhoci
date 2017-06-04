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


def setup_db_create_subparser(subparsers, parent_parser):
    """Adds db create sub-parser"""

    db_create_parser = subparsers.add_parser(
        "create", parents=[parent_parser])

    db_create_parser.add_argument(
        '--all', '-a', action='store_true')


def setup_db_drop_subparser(subparsers, parent_parser):
    """Adds db drop sub-parser"""

    db_drop_parser = subparsers.add_parser(
        "drop", parents=[parent_parser])

    db_drop_parser.add_argument(
        '--all', '-a', action='store_true')


def create():
    """Returns argparse parser."""

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--debug', required=False, action='store_true',
                               dest="debug", help='Turn DEBUG on')

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="parser")

    setup_db_create_subparser(subparsers, parent_parser)
    setup_db_drop_subparser(subparsers, parent_parser)

    return parser
