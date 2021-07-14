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

from elasticsearch import Elasticsearch
import re
import yaml

from rhoci.database import Database


class DFG(object):

    def __init__(self, name, squads=[], components=[],
                 squad_to_components={}):
        self.name = name
        self.squads = squads
        self.components = components
        self.squad_to_components = squad_to_components

    def insert(self):
        """Inserts object to the database."""
        if not Database.find_one("DFGs", {"name": self.name}):
            Database.insert(collection='DFGs',
                            data=self.json())

    def json(self):
        return {
            'name': self.name,
            'squads': self.squads,
            'components': self.components,
            'squad_to_components': self.squad_to_components,
        }

    @classmethod
    def get_all_DFGs_based_on_jobs(cls):
        """Returns a list of all DFGs based on job model where it cuts the
        DFG name from the job name and makes sure the set is unique.
        """
        DFGs = []
        with open(r'/etc/arie.yaml') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        es = Elasticsearch(data['elk']['es_url'])
        body = {
            "size": 0,
            "aggs" : {
                "jobs" : {
                    "terms" : { "field" : "DFG.keyword",  "size" : 4000 }
                }
            }
        }
        result = es.search(index="logstash", body=body)
        for bucket in result["aggregations"]['jobs']['buckets']:
            DFGs.append(bucket['key'])
        return DFGs

    @classmethod
    def get_all_squads(cls):
        squads = []
        for DFG_db in cls.find():
            if DFG_db['squads']:
                squads.extend(DFG_db['squads'])
        return squads

    @classmethod
    def get_all_components(cls):
        components = []
        for DFG_db in cls.find():
            if DFG_db['components']:
                components.extend(DFG_db['components'])
        return components

    @classmethod
    def get_squad(cls, DFG_name, component):
        DFG_db = cls.find_one(name=DFG_name)
        if DFG_db['squad_to_components']:
            for squad, components in DFG_db['squad_to_components'].items():
                for comp in components:
                    if comp == component:
                        return squad
                if component == components:
                    return squad
            return

    @classmethod
    def get_squad_components(cls, DFG_name, squad):
        """Returns all the components of a given squad."""
        DFG_db = cls.find_one(name=DFG_name)
        return DFG_db['squad_to_components'][squad]

    @classmethod
    def find(cls):
        """Returns find query."""
        query = {}
        DFGs = Database.find(collection="DFGs", query=query)
        return DFGs

    @classmethod
    def find_one(cls, name):
        """Returns one query result."""
        query = {}
        if name:
            query['name'] = name
        DFGs = Database.find_one(collection="DFGs", query=query)
        return DFGs

    @classmethod
    def count(cls, squads=False):
        """Returns the count of DFGs documents."""
        query = {}
        if squads:
            return len(cls.get_all_squads())
        else:
            DFGs = Database.find(collection='DFGs', query=query)
        return DFGs.count()
