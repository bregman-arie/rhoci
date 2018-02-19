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
import re


RELEASE_MAP = {'6': 'juno',
               '7': 'kilo',
               '8': 'liberty',
               '9': 'mitaka',
               '10': 'newton',
               '11': 'ocata',
               '12': 'pike',
               '13': 'queens'}


def extract_release(string):
    m = re.search('-\d{1,2}', string)
    return m.group().split('-')[1] if m else 0


def get_last_release():
    """Return last release number."""
    return db.session.query(db.func.max(Release.number)).scalar()
