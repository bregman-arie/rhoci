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

DFGs = [{'name': 'network', 'squads': [
    {'name': 'vNES', 'components': ['neutron', 'python-neutronclient']},
    {'name': 'octavia', 'components': ['octavia', 'neutron-lbaas']},
    {'name': 'ovn', 'components': ['networking-ovn']}]},
    {'name': 'storage', 'squads': [
        {'name': 'cinder', 'components': [
            'cinder',
            'python-os-brick', 'python-cinderclient']},
        {'name': 'glance', 'components': [
            'glance',
            'glance_store', 'python-glanceclient']},
        {'name': 'manila', 'components': ['manila', 'python-manilaclient']},
        {'name': 'sahara', 'components': ['sahara', 'python-saharaclient']},
        {'name': 'swift', 'components': ['swift', 'python-swiftclien']}]}]
