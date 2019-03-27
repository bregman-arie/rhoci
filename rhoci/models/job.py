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

    def __init__(self, _class, name, last_build, properties={}):
        self.builds = []
        self.tests = []
        if last_build:
            last_build.pop('artifacts')
            self.last_build = last_build
            if 'timestamp' in self.last_build:
                self.last_build['timestamp'] = datetime.datetime.fromtimestamp(
                    int(self.last_build['timestamp'] / 1000))
            self.builds.append(last_build)
        else:
            self.last_build = {'result': None, 'number': None}
        self.properties = properties
        self._class = _class
        self.name = name
        self.created_at = datetime.datetime.utcnow()

    def insert(self):
        job = Database.find_one("jobs", {"name": self.name})
        if not job:
            Database.insert(collection='jobs', data=self.json())
        else:
            Database.DATABASE['jobs'].find_one_and_update(
                {"name": self.name},
                {"$set": {"last_build": self.last_build}})
            Database.DATABASE['jobs'].update(
                {"name": self.name},
                {"$addToSet": {"builds": self.last_build}})

    def json(self):
        return {
            '_class': self._class,
            'name': self.name,
            'last_build': self.last_build,
            'created_at': self.created_at,
            'builds': self.builds,
            'tests': self.tests,
            'properties': self.properties
        }

    @classmethod
    def count(cls, name_regex=None, last_build_res=None):
        """Returns counts of jobs based on passed arguments."""
        query = {}
        if name_regex:
            regex = re.compile(name_regex, re.IGNORECASE)
            query['name'] = regex
        if last_build_res:
            query['last_build.result'] = last_build_res
        jobs = Database.find(collection='jobs', query=query)
        return jobs.count()

    @classmethod
    def find(cls, name_regex=None, last_build_result=None, properties=None):
        """Returns find query."""
        query = {}
        if name_regex:
            regex = re.compile(name_regex, re.IGNORECASE)
            query['name'] = regex
        if last_build_result:
            query['last_build.result'] = last_build_result
        if properties:
            for k, v in properties.items():
                query['properties.{}'.format(k)] = v
        jobs = Database.find(collection="jobs", query=query)
        return jobs
