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

import pymongo


class Database(object):

    URI = "mongodb://127.0.0.1:27017"
    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client['rhoci']

    @staticmethod
    def insert(collection, data):
        _id = Database.DATABASE[collection].insert(data)
        return _id

    @staticmethod
    def find(collection, query, projection=None):
        return Database.DATABASE[collection].find(query, projection)

    @staticmethod
    def find_one(collection, query, projection=None):
        return Database.DATABASE[collection].find_one(query, projection)

    @staticmethod
    def delete_one(collection, query):
        return Database.DATABASE[collection].delete_one(query)
