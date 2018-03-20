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

from rhoci import models


logger = logging.getLogger(__name__)

dfg = Blueprint('dfg', __name__)


@dfg.route('/', methods=['GET'])
def index():

    db_dfg = models.DFG.query.all()
    all_dfgs = [dfg.serialize for dfg in db_dfg]

    return render_template('DFGs.html', all_dfgs=all_dfgs)


@dfg.route('/squads', methods=['GET'])
def squads():

    db_squads = models.Squad.query.all()
    all_squads = [squad.serialize for squad in db_squads]

    return render_template('DFGs.html', all_dfgs=all_squads)


@dfg.route('/squad/<squad_name>', methods=['GET'])
def squad_summary(squad_name):
    pass


@dfg.route('/component/<comp_name>', methods=['GET'])
def component_summary(comp_name):
    pass


@dfg.route('/<dfg_name>', methods=['GET'])
def stats(dfg_name):

    agent = models.Agent.query.one()
    rls = models.Release.query.all()
    dfg = models.DFG.query.filter_by(name=dfg_name).first()
    data = []
    for item in rls:
        data.append({'FAILURE': models.Job.query.filter(
            models.Job.name.contains(
                'DFG-%s' % dfg_name), models.Job.last_build_result.like(
                    'FAILURE'), models.Job.release == item).count(),
            'SUCCESS': models.Job.query.filter(
                models.Job.name.contains(
                    'DFG-%s' % dfg_name), models.Job.last_build_result.like(
                        'SUCCESS'), models.Job.release == item).count(),
            'UNSTABLE': models.Job.query.filter(
                models.Job.name.contains(
                    'DFG-%s' % dfg_name), models.Job.last_build_result.like(
                        'UNSTABLE'), models.Job.release == item).count(),
            'ABORTED': models.Job.query.filter(
                models.Job.name.contains(
                    'DFG-%s' % dfg_name), models.Job.last_build_result.like(
                        'ABORTED'), models.Job.release == item).count(),
            'None': models.Job.query.filter(
                models.Job.name.contains(
                    'DFG-%s' % dfg_name), models.Job.last_build_result.like(
                        'None'), models.Job.release == item).count(),
            'number': item.number,
            'dfg': dfg_name})

    return render_template('DFG_stats.html', releases=data, agent=agent,
                           dfg=dfg)
