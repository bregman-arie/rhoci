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
from migrate.versioning import api
import os.path


def setup_versioning(config):
    """Setup versioning for easy DB updates."""
    if not os.path.exists(config['SQLALCHEMY_MIGRATE_REPO']):
        api.create(config['SQLALCHEMY_MIGRATE_REPO'], 'database repository')
        api.version_control(config['SQLALCHEMY_DATABASE_URI'],
                            config['SQLALCHEMY_MIGRATE_REPO'])
    else:
        api.version_control(config['SQLALCHEMY_DATABASE_URI'],
                            config['SQLALCHEMY_MIGRATE_REPO'],
                            api.version(config['SQLALCHEMY_MIGRATE_REPO']))
