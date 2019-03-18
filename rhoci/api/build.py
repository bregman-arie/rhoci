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

from flask import jsonify
import logging

from rhoci.models.build import Build

LOG = logging.getLogger(__name__)

from rhoci.api import bp  # noqa


@bp.route('/builds/all')
def all_builds():
    """All builds API route."""
    results = {'data': []}
    builds = Build.find()
    for build in builds:
        print(build)
        results['data'].append('bla1', 'bla2')

    return jsonify(results)
