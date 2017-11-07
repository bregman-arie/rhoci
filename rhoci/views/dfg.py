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

from rhoci.models import DFG


logger = logging.getLogger(__name__)

dfg = Blueprint('dfg', __name__)


@dfg.route('/', methods=['GET'])
def index():

    db_dfg = DFG.query.all()
    all_dfgs = [dfg.serialize for dfg in db_dfg]

    return render_template('DFGs.html', all_dfgs=all_dfgs)


@dfg.route('/dfg/<dfg_name>', methods=['GET'])
def stats(dfg_name):

    print dfg_name
    return render_template('DFG_stats.html')
