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
from __future__ import division

from rhoci.database import Database

import datetime


class Build(object):

    COLLECTION = 'builds'

    def __init__(self, job_name, number, result, timestamp):
        self.job_name = job_name
        self.number = number
        self.result = result
        self.date = datetime.datetime.fromtimestamp(
            int(timestamp / 1000))

    def insert(self):
        if not Database.find_one(self.COLLECTION, {"number": self.number,
                                 "job_name": self.job_name}):
            Database.insert(collection=self.COLLECTION,
                            data=self.json())

    def json(self):
        return {
            'number': self.number,
            'job_name': self.job_name,
            'result': self.result,
            'date': self.date,
        }

    @classmethod
    def find(cls):
        """Returns find query."""
        query = {}
        builds = Database.find(collection="builds", query=query)
        return builds

    @classmethod
    def count(cls):
        """Returns the count of builds documents."""
        query = {}
        builds = Database.find(collection='builds', query=query)
        return builds.count()

    @classmethod
    def get_builds_count_per_date(num_of_days=10):
        """Returns a list of date and builds count."""
        builds = []
        dates = []
        pipeline = [
            {"$group":
             {"_id": {"$add": [{"$dayOfYear": "$date"},
                               {"$multiply": [400, {"$year": "$date"}]}]},
              "builds": {"$sum": 1}, "first": {
                  "$min": "$date"}}}, {"$sort": {
                      "_id": -1}}, {"$limit": 10}, {
                          "$project": {
                              "date": "$first", "builds": 1, "_id": 0}}]
        cursor = Database.DATABASE['builds'].aggregate(pipeline)  # noqa
        for build_date in cursor:
            dates.append((build_date['date'].strftime("%m/%d/%Y")))
            builds.append(build_date['builds'])
        return builds, dates
