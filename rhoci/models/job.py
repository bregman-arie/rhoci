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

    def __init__(self, name, last_build, **kwargs):
        self.builds = []
        self.tests = []
        self.last_successful_build = None
        if last_build:
            # TODO(abregman): some artifacts start with dot (e.g. ".envrc")
            # MongoDB doesn't allow that. Will have to find a solution.
            if 'artifacts' in last_build:
                last_build.pop('artifacts')
            if 'status' in last_build and last_build['status'] == "SUCCESS":
                self.last_successful_build = last_build
            self.last_build = last_build
            self.builds.append(last_build)
        else:
            self.last_build = {'status': "None", 'number': None}
        self.name = name
        self.created_at = datetime.datetime.utcnow()
        self.properties = kwargs
        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

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
                {"$set": {**self.properties,
                          "last_build": self.last_build}})

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
        if build['status'] == "SUCCESS":
            Database.DATABASE['jobs'].find_one_and_update(
                {"name": job_name},
                {"$set": {"last_successful_build": build}})

    def json(self):
        return self.__dict__

    @classmethod
    def count(cls, name=None, last_build_res=None):
        """Returns number of jobs based on passed arguments."""
        query = {}
        if name:
            regex = re.compile(name, re.IGNORECASE)
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
    def find(cls, name=None, exact_match=False,
             last_build_result=None, **kwargs):
        """Returns find query."""
        query = {}
        if name and not exact_match:
            regex = re.compile(name, re.IGNORECASE)
            query['name'] = regex
        elif name:
            query['name'] = name
        if last_build_result:
            query['last_build.result'] = last_build_result
        for k, v in kwargs.items():
            query[k] = v
        jobs = list(Database.find(collection="jobs", query=query))
        return jobs

    @classmethod
    def delete_one(cls, name):
        """Deletes one job document from the database."""
        query = {"name": name}
        Database.delete_one("jobs", query)

    @classmethod
    def get_builds_count_per_date(num_of_days=10):
        """Returns a list of date and builds count."""
        builds = []
        dates = []
        pipeline = [
            {"$project": {"_id": 0, "builds": 1}},
            {"$unwind": "$builds"},
            # {"$group": {"_id": "$builds.timestamp", "count": {"$sum": 1}}},
            {"$group": {"_id": {"$add": [
                {"$dayOfYear": "$builds.timestamp"},
                {"$multiply": [400, {"$year": "$builds.timestamp"}]}]},
                "builds": {"$sum": 1},
                "first": {"$min": "$builds.timestamp"}}},
            {"$sort": {"builds": -1}},
            {"$limit": 10}
        ]
        cursor = Database.DATABASE['jobs'].aggregate(pipeline)  # noqa
        for build_date in cursor:
            if build_date['first']:
                dates.append((build_date['first'].strftime("%m/%d/%Y")))
                builds.append(build_date['builds'])
        return builds, dates
