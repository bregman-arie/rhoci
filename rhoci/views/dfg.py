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

    return render_template('DFG/all_cards.html', all_dfgs=all_dfgs)


@dfg.route('/squads', methods=['GET'])
def squads():

    db_squads = models.Squad.query.all()
    all_squads = [squad.serialize for squad in db_squads]

    return render_template('DFG/squad/all_cards.html', all_squads=all_squads)


@dfg.route('/components', methods=['GET'])
def components():

    db_squads = models.Squad.query.all()
    components = [comp for squad in db_squads for comp in squad.components]

    return render_template('DFG/component/all_cards.html',
                           components=components)


@dfg.route('/<dfg_name>/squad/<squad_name>', methods=['GET'])
def squad_summary(squad_name, dfg_name):
    agent = models.Agent.query.one()
    squad = models.Squad.query.filter_by(name=squad_name).first()
    components = squad.components
    data = []
    releases = models.Release.query.all()
    total_number = 0

    for rel in releases:
        data.append({'number': rel.number, 'dfg': dfg_name})

        for status in ['FAILURE', 'SUCCESS', 'ABORTED', 'UNSTABLE', 'None']:
            num_of_jobs = 0
            for component in components:
                count = models.Job.query.filter(models.Job.name.contains(
                    'DFG-%s-%s' % (dfg_name, component.name)),
                    models.Job.last_build_result.like(status),
                    models.Job.release_number == rel.number).count()
                num_of_jobs = num_of_jobs + count
            data[-1][status] = num_of_jobs
            total_number = total_number + num_of_jobs
        data[-1]['num_of_jobs'] = total_number

    return render_template('DFG/squad/summary.html', releases=data,
                           agent=agent, dfg=dfg)


@dfg.route('/<dfg_name>/component/<component_name>', methods=['GET'])
def component_summary(component_name, dfg_name):

    agent = models.Agent.query.one()
    releases = models.Release.query.all()
    dfg = models.DFG.query.filter_by(name=dfg_name).first()
    data = []

    for rel in releases:
        data.append({'number': rel.number, 'dfg': dfg_name,
                     'num_of_jobs': models.Job.query.filter(
                         models.Job.name.contains(
                             'DFG-%s-%s' % (dfg_name, component_name)),
                         models.Job.release == rel).count()})
        for status in ['FAILURE', 'SUCCESS', 'ABORTED', 'UNSTABLE', 'None']:
            data[-1][status] = models.Job.query.filter(
                models.Job.name.contains(
                    'DFG-%s-%s' % (dfg_name, component_name)),
                models.Job.last_build_result.like(
                    status), models.Job.release == rel).count()

    return render_template('DFG/component/summary.html', releases=data,
                           agent=agent, dfg=dfg)


@dfg.route('/<dfg_name>', methods=['GET'])
def stats(dfg_name):
    """
    data = [{'number': 10, FAILURE: 200, ... }, {'number': 11}]
    """

    agent = models.Agent.query.one()
    releases = models.Release.query.all()
    dfg = models.DFG.query.filter_by(name=dfg_name).first()
    data = []

    for rel in releases:
        data.append({'number': rel.number, 'dfg': dfg_name,
                     'num_of_jobs': models.Job.query.filter(
                         models.Job.name.contains('DFG-%s' % dfg_name),
                         models.Job.release == rel).count()})
        for status in ['FAILURE', 'SUCCESS', 'ABORTED', 'UNSTABLE', 'None']:
            data[-1][status] = models.Job.query.filter(
                models.Job.name.contains(
                    'DFG-%s' % dfg_name), models.Job.last_build_result.like(
                        status), models.Job.release == rel).count()

    return render_template('DFG/summary.html', releases=data, agent=agent,
                           dfg=dfg)
