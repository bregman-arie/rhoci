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


class Config(object):
    """RHOCI server configuration."""

    RHOCI_SERVER_PORT = 5000
    RHOCI_DEBUG = False
    RHOCI_CONFIG_FILE = '/etc/rhoci/server.conf'
    RHOCI_SERVER_LOG = 'rhoci.log'
    RHOCI_RELEASES = '6,7,8,9,10,11,12,13'
    RHOCI_UPDATE_INTERVAL = 3600
