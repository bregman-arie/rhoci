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

import logging
import os
import yaml

LOG = logging.getLogger(__name__)


class Config():

    CONF_LOC = [os.path.expanduser('~'),
                '/etc/rhoci']
    CONF_NAME = 'rhoci.conf'

    def __init__(self, config_file=None):
        self.config_file = self.get_config_file(config_file)
        self.config = self.load_configuration()

    @staticmethod
    def search_in_paths(paths, file_name):
        """Returns file full path if found."""
        for path in paths:
            f = os.path.join(path, file_name)
            if os.path.isfile(f):
                return f

    def get_config_file(self, config_file):
        """Returns config file."""
        if config_file:
            if os.path.isfile(config_file):
                conf = config_file
            else:
                conf = self.search_in_paths(self.CONF_LOC, self.CONF_NAME)
        else:
            conf = self.search_in_paths(self.CONF_LOC, self.CONF_NAME)
        return conf

    def load_configuration(self):
        """Returns loaded YAML stream."""
        with open(self.config_file, 'r') as stream:
            conf = yaml.load(stream)
            return conf
