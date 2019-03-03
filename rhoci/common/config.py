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
import logging

LOG = logging.getLogger(__name__)


class Config():

    def __init__(self, config_file=None):
        self.config_file = self.get_config_file(config_file)
        self.config = self.load_configuration()

    def get_config_file(config_file):
        """Returns config file."""
        pass

    def load_configuration(self):
        """Returns loaded YAML stream."""
        with open(self.config_file, 'r') as stream:
            pass
