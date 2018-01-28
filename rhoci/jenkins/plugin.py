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


def insert_plugin_data_into_db(plugin):
    """Inserts a given plugin to the database."""
    plugin_name = plugin[1]['longName']
    if not models.Plugin.query.filter_by(name=plugin_name).count():
        db_plugin = models.Plugin(name=plugin_name)
        db.session.add(db_plugin)
        db.session.commit()


def populate_db_with_plugins(agent):
    """Adds all plugins from Jenkins to the DB."""
    conn = jenkins.Jenkins(agent.url, agent.user, agent.password)
    plugins = conn.get_plugins()

    for plugin in plugins.iteritems():
        insert_plugin_data_into_db(plugin)
