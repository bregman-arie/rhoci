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

    def __init__(self, name, last_build, properties={}):
        self.builds = []
        self.tests = []
        if last_build:
            # TODO(abregman): some artifacts start with dot (e.g. ".envrc")
            # MongoDB doesn't allow that. Will have to find a solution.
            if 'artifacts' in last_build:
                last_build.pop('artifacts')
            self.last_build = last_build
            self.builds.append(last_build)
        else:
            self.last_build = {'status': "None", 'number': None}
        self.properties = properties
        self.name = name
        self.created_at = datetime.datetime.utcnow()

    def insert(self):
        job = Database.find_one("jobs", {"name": self.name})
        if not job:
            Database.insert(collection='jobs', data=self.json())
        else:
            if not Database.DATABASE['jobs'].find_one(
                {"builds.number": self.last_build['number'],
                 "name": self.name}):
                Database.DATABASE['jobs'].update(
                    {"name": self.name},
                    {"$addToSet": {"builds": self.last_build}})
            Database.DATABASE['jobs'].find_one_and_update(
                {"name": self.name},
                {"$set": {"last_build": self.last_build}})

    @classmethod
    def update_build(cls, job_name, build):
        # If new build, add it to the array of builds
        if not Database.DATABASE['jobs'].find_one(
            {"builds.number": build['number'],
             "name": job_name}):
            Database.DATABASE['jobs'].update(
                {"name": job_name},
                {"$addToSet": {"builds": build}})
        else:
            Database.DATABASE['jobs'].update(
                {"name": job_name, "builds.number": build['number']},
                {"$set": {"builds.$": build}})
        # If last build, update last build reference
        job = Database.DATABASE['jobs'].find_one({"name": job_name})
        if build['number'] >= job['last_build']['number']:
            Database.DATABASE['jobs'].find_one_and_update(
                {"name": job_name},
                {"$set": {"last_build": build}})

    def json(self):
        return {
            'name': self.name,
            'last_build': self.last_build,
            'created_at': self.created_at,
            'builds': self.builds,
            'tests': self.tests,
            'properties': self.properties
        }

    @classmethod
    def count(cls, name_regex=None, last_build_res=None):
        """Returns number of jobs based on passed arguments."""
        query = {}
        if name_regex:
            regex = re.compile(name_regex, re.IGNORECASE)
            query['name'] = regex
        if last_build_res:
            query['last_build.status'] = last_build_res
        jobs = Database.find(collection='jobs', query=query)
        return jobs.count()

    @classmethod
    def count_builds(cls):
        """Returns the number of builds."""
        builds_count = 0
        pipeline = [
            {"$project": {"num_of_builds": {"$size": "$builds"}}},
            {"$group": {"_id": None, "count": {"$sum": "$num_of_builds"}}}
        ]
        cursor = Database.DATABASE['jobs'].aggregate(pipeline)  # noqa
        for data in cursor:
            builds_count = data['count']
        return builds_count

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
        jobs = list(Database.find(collection="jobs", query=query))
        return jobs

    @classmethod
    def get_builds_count_per_date(num_of_days=10):
        """Returns a list of date and builds count."""
        builds = []
        dates = []
        pipeline = [{"$unwind": "$builds"},
                    {"$group":
                     {"_id": {"$add": [
                         {"$dayOfYear": "$last_build.timestamp"},
                         {"$multiply": [400, {
                             "$year": "$last_build.timestamp"}]}]},
                      "builds": {"$sum": 1}, "first": {
                          "$min": "$last_build.timestamp"}}}, {"$sort": {
                              "_id": -1}}, {"$limit": 10}, {
                                  "$project": {
                                      "timestamp": "$first",
                                      "builds": 1, "_id": 0}}]
        cursor = Database.DATABASE['jobs'].aggregate(pipeline)  # noqa
        for build_date in cursor:
            dates.append((build_date['timestamp'].strftime("%m/%d/%Y")))
            builds.append(build_date['builds'])
        return builds, dates
