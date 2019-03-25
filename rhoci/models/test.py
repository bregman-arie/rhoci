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

from rhoci.database import Database


class Test(object):

    COLLECTION = 'tests'

    def __init__(self, build_number, job_name):
        self.build_number = build_number
        self.job_name = job_name

    def insert(self):
        if not Database.find_one(self.COLLECTION,
                                 {"build_number": self.build_number,
                                  "job_name": self.job_name}):
            Database.insert(collection='builds',
                            data=self.json())

    def json(self):
        return {
            'build_number': self.build_number,
            'job_name': self.job_name,
        }

    @classmethod
    def find(cls):
        """Returns find query."""
        query = {}
        tests = Database.find(collection=cls.COLLECTION, query=query)
        return tests

    @classmethod
    def count(cls):
        """Returns the count of builds documents."""
        query = {}
        builds = Database.find(collection='builds', query=query)
        return builds.count()
