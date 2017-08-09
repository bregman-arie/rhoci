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
from flask import Blueprint
from flask import render_template
import logging


logger = logging.getLogger(__name__)

review_statistics = Blueprint('review_statistics', __name__)


@review_statistics.route('/review_statistics', methods=['GET', 'POST'])
def index():
    """Code Review Statistics page."""
    return render_template('review_statistics.html')
