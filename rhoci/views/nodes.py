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
from flask import render_template
from flask import Blueprint
import logging

from rhoci.models import Node


logger = logging.getLogger(__name__)

nodes = Blueprint('nodes', __name__)


@nodes.route('/')
def index():
    """RHOSP Jenkins Nodes page."""
    nodes = Node.query.all()
    return render_template('nodes.html', nodes=nodes)
