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
from rhoci.db.base import db


class Agent(db.Model):
    """Represents Jenkins agent/connection."""

    __tablename__ = 'agent'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    number_of_jobs = db.Column(db.Integer)
    number_of_nodes = db.Column(db.Integer)
    number_of_plugins = db.Column(db.Integer)

    def __repr__(self):
        return "<Agent %r\nNumber of jobs: %s\nNumber of \
nodes: %s\nNumber of plugins: %s" % (self.name, self.number_of_jobs,
                                     self.number_of_nodes,
                                     self.number_of_plugins)
