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
from flask.ext.autodoc import Autodoc
from flask import Blueprint
import logging

logger = logging.getLogger(__name__)

doc = Blueprint('doc', __name__, url_prefix='/doc')
auto = Autodoc()


@doc.route('/')
@doc.route('/public')
def public_doc():
    return auto.html(groups=['public'], title='RHOCI API Documentation')
