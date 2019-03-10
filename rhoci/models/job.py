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

import datetime
import re

from rhoci.database import Database


class Job(object):

    def __init__(self, _class, name, last_build, _id=None):
        self._class = _class
        self.name = name
        self._id = _id
        self.last_build = last_build
        self.created_date = datetime.datetime.utcnow()

    def save_to_db(self):
        if not Database.find_one("jobs", {"name": self.name}):
            Database.insert(collection='jobs',
                            data=self.json())

    def json(self):
        return {
            '_class': self._class,
            'name': self.name,
            '_id': self._id,
            'last_build': self.last_build,
            'created_date': self.created_date
        }

    @classmethod
    def get_all_DFGs(self):
        """Returns list of all DFGs based on jobs names.
        all_DFGs = [{'name': network, 'num_of_jobs': 20}, ...]
        """
        DFGs = []
        regex = re.compile('DFG-', re.IGNORECASE)
        DFG_jobs = Database.find(collection='jobs',
                                 query={'name': regex})
        for job in DFG_jobs:
            jname = job['name']
            DFG_name = jname.split('-')[1] if '-' in jname else jname
            if DFG_name not in DFGs:
                DFGs.append(DFG_name)
        return DFGs

    @classmethod
    def count(cls, name_regex, last_build_res):
        """Returns counts of jobs based on passed arguments."""
        query = {}
        if name_regex:
            regex = re.compile(name_regex, re.IGNORECASE)
            query['name'] = regex
        if last_build_res:
            query[last_build_res] = last_build_res
        jobs = Database.find(collection='jobs', query=query)
        return jobs.count()
