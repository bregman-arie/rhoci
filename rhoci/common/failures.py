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
FAILURES = [
    {'category': 'Packages',
     'pattern': 'ImportError: No module named',
     'upper_bound_pattern': 'Traceback',
     'lower_bound_pattern': None,
     'action': 'Install the missing package on the slave or the remote host',
     'cause': 'The node you invoked the command on is missing a package'
     },

    {'category': 'Permissions',
     'pattern': 'not writable',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': None,
     'action': 'Add write permissions to the path you are trying to use',
     'cause': 'The path you are trying to use is missing permissions',
     },
]
