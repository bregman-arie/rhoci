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
import rhoci.jenkins.constants as jenkins_const


class Job(object):

    def __init__(self, name, last_build, **kwargs):
        self.builds = []
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
            # Check if last build is in job builds. If not, add it.
            if not Database.DATABASE['jobs'].find_one(
                {"builds.number": self.last_build['number'],
                 "name": self.name}):
                Database.DATABASE['jobs'].update(
                    {"name": self.name},
                    {"$addToSet": {"builds": self.last_build}})
            # Update job
            # Database.DATABASE['jobs'].find_one_and_update(
            #    {"name": self.name},
            #    {"$set": self.properties})
            Database.DATABASE['jobs'].find_one_and_update(
                {"name": self.name},
                {"$set": {'lol': 'lol2'}})

    @classmethod
    def update_tests(cls, job_name, build_num, tests):
        """Add tests to build."""
        Database.DATABASE['jobs'].find_one_and_update(
            {"name": job_name, "builds.number": int(build_num)},
            {"$set": {"builds.$.tests": tests}})

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
        if 'status' in build:
            if build['status'] == "SUCCESS":
                Database.DATABASE['jobs'].find_one_and_update(
                    {"name": job_name},
                    {"$set": {"last_successful_build": build}})

    def json(self):
        return self.__dict__

    @classmethod
    def count(cls, name=None, last_build_res=None, DFG=None, release=None,
              squad=None, component=None, query_str=None):
        """Returns number of jobs based on passed arguments."""
        query = {}
        if name:
            regex = re.compile(name, re.IGNORECASE)
            query['name'] = regex
        if last_build_res:
            query['last_build.status'] = last_build_res
        if DFG:
            query['DFG'] = DFG
        if squad:
            query['squad'] = squad
        if component:
            query['component'] = component
        if release:
            query['release'] = release
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
             last_build_result=None, projection=None,
             build_number=None, query_str=None, **kwargs):
        """Returns find query."""
        query = {}
        if (name or (query_str and "name" in query_str)) and not exact_match:
            regex = re.compile(name or query_str['name'], re.IGNORECASE)
            query['name'] = regex
        elif name:
            query['name'] = name
        if build_number:
            query['builds.number'] = build_number
        if last_build_result:
            query['last_build.result'] = last_build_result
        for k, v in kwargs.items():
            query[k] = v
        if query_str and "last_added" not in query_str:
            if "name" in query_str:
                regex = re.compile(query_str['name'], re.IGNORECASE)
                query_str['name'] = regex
            query = query_str
        if query_str and "last_added" in query_str:
            jobs = list(Database.find(collection="jobs", query={'last_build.status': 'None', 'release': "15"},
                                      projection=projection).limit(10))
        else:
            jobs = list(Database.find(collection="jobs", query=query,
                                      projection=projection))
        return jobs

    @classmethod
    def delete_one(cls, name):
        """Deletes one job document from the database."""
        query = {"name": name}
        Database.delete_one("jobs", query)

    @classmethod
    def get_builds_count_per_release(cls, DFG=None, squad=None,
                                     component=None):
        pie = {}
        for rel in jenkins_const.RELEASES:
            pie[rel] = {}
            for res in jenkins_const.RESULTS:
                pie[rel][res] = Job.count(
                    last_build_res=res, DFG=DFG, release=rel,
                    component=component, squad=squad)
        return pie

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
