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
    {'category': 'CI framework',
     'name': 'Missing module',
     'pattern': 'No module',
     'upper_bound_pattern': 'Traceback',
     'lower_bound_pattern': '',
     'action': 'Install the missing package on the " \
"host where you recieved the error',
     'cause': 'The node you invoked the command on is missing a package'
     },

    {'category': 'CI framework',
     'name': 'Missing permissions',
     'pattern': 'not writable',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Add write permissions to the path you are trying to use',
     'cause': 'The path you are trying to use is missing permissions',
     },

    {'category': 'CI framework',
     'name': 'Missing Templates',
     'pattern': 'missing_templates',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Specify the right template name/path',
     'cause': 'You specified non-existing template',
     },

    {'category': 'Product',
     'name': 'Deployment Failure',
     'pattern': 'deployment failed',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Read /home/stack/overcloud_failure_long.log to find " \
"out why the deployment failed',
     'cause': 'The failure message is to generic to point " \
"out why exactly the deployment failed',
     },

    {'category': 'Product',
     'name': 'Bad URL',
     'pattern': '404 Client Error',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Change URL to one that actually works',
     'cause': 'The specified URL was not found (404)',
     },

]
