# Copyright 2018 Arie Bregman
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
import jenkins
import logging

from rhoci.db.base import db
import rhoci.models as models

LOG = logging.getLogger(__name__)


def insert_node_data_into_db(node):
    """Inserts a given node to the database."""
    if not models.Node.query.filter_by(name=node['name']).count():
        db_node = models.Node(name=node['name'])
        db.session.add(db_node)
        db.session.commit()


def populate_db_with_nodes(agent):
    """Adds all nodes from Jenkins to the DB."""
    conn = jenkins.Jenkins(agent.url, agent.user, agent.password)
    nodes = conn.get_nodes()

    for node in nodes:
        insert_node_data_into_db(node)
