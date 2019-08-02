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

from flask import current_app as app
from flask import render_template
from flask import url_for
import logging

LOG = logging.getLogger(__name__)

from rhoci.test import bp  # noqa


@bp.route('/index')
@bp.route('/')
def index():
    """All tests."""
    jenkins_url = app.config['custom']['jenkins']['url']
    uf = url_for('api.all_tests')
    return render_template('tests/index.html',
                           jenkins_url=jenkins_url,
                           uf=uf)


@bp.route('/<name>')
def test(name):
    """Specific test summary."""
    return render_template('tests/one_test_summary.html')
