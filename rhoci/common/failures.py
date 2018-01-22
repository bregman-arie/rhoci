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
     'action': 'Install the missing package on the ' +
     'host where you recieved the error',
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
     'action': 'Read /home/stack/overcloud_failure_long.log to find ' +
     'out why the deployment failed',
     'cause': 'The failure message is to generic to point ' +
     'out why exactly the deployment failed',
     },

    {'category': 'Product',
     'name': 'Bad URL',
     'pattern': '404 Client Error',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Change URL to one that actually works',
     'cause': 'The specified URL was not found (404)',
     },

    {'category': 'Product',
     'name': 'Image not found',
     'pattern': 'docker pull failed',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Make sure image exists and retrigger build',
     'cause': 'You tried to use docker image that doesnt exists',
     },

    {'category': 'Product',
     'name': 'PEP8 Failure',
     'pattern': 'pep8: commands failed',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Fix the PEP8 failures in pep8 log file',
     'cause': 'There are several Python styling issues with the code',
     },

    {'category': 'Wrong Usage',
     'name': 'Unrecognized Arguments',
     'pattern': 'unrecognized arguments',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Fix the command to use existing arguments',
     'cause': 'You specified non-existing arguments',
     },

    {'category': 'Product',
     'name': 'Overcloud Deploment - Missing Stack',
     'pattern': 'The Stack (overcloud) could not be found',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Take a deeper look at /home/stack/overcloud_failure_long.log',
     'cause': 'Probably not enough resources to deploy Overcloud',
     },

    {'category': 'Infrastructure',
     'name': 'Service Unavailable',
     'pattern': 'Service Unavailable',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Contact the support team of the service you are trying to use',
     'cause': 'The service you are trying to reach is unavailable',
     },

    {'category': 'Infrastructure',
     'name': 'Server Unavailable',
     'pattern': 'Gateway Time-out',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Contact the support team of the service you are trying to use',
     'cause': 'The server you are trying to reach is unavailable',
     },

    {'category': 'Infrastructure',
     'name': 'Server Unavailable',
     'pattern': 'Timeout waiting for the server',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Contact the support team of the service you are trying to use',
     'cause': 'The server you are trying to reach is unavailable',
     },

    {'category': 'Product',
     'name': 'Overcloud Upgrade',
     'pattern': 'Overcloud upgrade composable step failed',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Read overcloud upgrade log for more details',
     'cause': 'Looks like overcloud upgrade failed',
     },

    {'category': 'Patching',
     'name': 'RPM Spec - SourcX and BuildArch',
     'pattern': 'BuildArch AFTER SourceX and PatchX',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Fix RPM spec by moving BuildArch after SourceX and PatchX',
     'cause': 'BuildArch is used before SourceX or PatchX in the RPM spec',
     },

    {'category': 'Patching',
     'name': 'Mockbuild Execution',
     'pattern': 'command failed: rhpkg mockbuild',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Make sure you have tags synched with upstream project',
     'cause': 'Mockbuild failed for unknown reason',
     },

    {'category': 'CI workflow',
     'name': 'Git failure',
     'pattern': 'possibly due to conflict resolution',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Make sure you clone the project the right ' +
     'way or cherry-pick commits',
     'cause': 'Mockbuild failed for unknown reason',
     },

    {'category': 'CI Workflow',
     'name': 'Git - Unable to fetch Repo',
     'pattern': 'Error fetching remote repo',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Make sure the repo name and branch are correct',
     'cause': 'It looks like you specified a missing repo or branch',
     },


    {'category': 'Infrastructure',
     'name': 'Internal Server Error',
     'pattern': 'Server Error for url',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Check if infrastructure is under maintenance. If not, ' +
     'please open a ticket for your support team.',
     'cause': 'Looks like internal error occurred in the server you are ' +
     'trying to reach',
     },

    {'category': 'Packages',
     'name': 'Missing Packages',
     'pattern': 'Error: Package:',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Make sure package is present in the repository or you have ' +
     'the right repository that should include the missing package',
     'cause': 'The package you are trying to install requires another ' +
     'package that is missing',
     },

    {'category': 'Jenkins',
     'name': 'Archive Issue',
     'pattern': 'We had issue(s) while log archiving',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'User - retrigger job. Admin - investigate Jenkins logs',
     'cause': 'Could not figure out why it happened',
     },

    {'category': 'Application',
     'name': 'Application Failure',
     'pattern': 'failed unexpectedly',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Check app logs to see why they failed',
     'cause': 'No idea :(',
     },

    {'category': 'Product',
     'name': 'Tests Failures',
     'pattern': 'The test run failed',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Fix the bugs in your project :)',
     'cause': 'No idea',
     },

    {'category': 'Infrastructure',
     'name': 'Timeout',
     'pattern': 'ERROR: Timeout after',
     'upper_bound_pattern': 'TASK [',
     'lower_bound_pattern': '',
     'action': 'Check if infrastructure is under maintenance. If not, ' +
     'please open a ticket for your support team.',
     'cause': 'Looks like there is something wrong with the server you are ' +
     'trying to reach',
     },
]
