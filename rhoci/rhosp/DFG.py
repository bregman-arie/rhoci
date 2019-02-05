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
from rhoci.db.base import db
# from rhoci.jenkins.job import get_count
from rhoci import models


DFGs = {
    'network': {
        'vNES': ['neutron', 'python-neutronclient'],
        'Octavia': ['octavia', 'neutron-lbaas'],
        'OVN': ['networking-ovn']}}


def get_DFG_name(string):
    """
    Receives string like 'DFG-network-neutron-12'

    Returns DFG name. In the example above: Network.
    """
    name = string.split('-')[1] if '-' in string else string
    return name.upper() if len(name) < 4 else name.capitalize()


def get_squad_name(string):
    """
    Receives string like 'DFG-network-neutron-12'

    Returns squad name. In the example above: neutron.
    """
    DFG = get_DFG_name(string)
    component = string.split('-')[2] if '-' in string else string
    if DFG.lower() in DFGs:
        for dfg, squads in DFGs.items():
            for squad, components in squads.items():
                for component in components:
                    if "dfg-%s-%s" % (DFG.lower(), component) in string:
                        return squad
    return


def dfg_exists(dfg):
    """Returns True if DFG exists in DB else returns False."""
    return (models.DFG.query.filter_by(name=dfg).count() or
            dfg.lower() == 'dfg')


def add_dfg_to_db(dfg):
    """Inserts DFG into DB."""
    db_dfg = models.DFG(name=dfg)
    db.session.add(db_dfg)
    db.session.commit()


def add_squad_to_db(squad, DFG):
    """Inserts squad into DB."""
    DFG_db = models.DFG.query.filter_by(name=DFG).first()
    db_squad = models.Squad(name=squad, DFG_name=DFG_db.name)
    db.session.add(db_squad)
    db.session.commit()


def add_components_to_db(components, squad):
    """Inserts components into DB."""
    squad_db = models.Squad.query.filter_by(name=squad).first()
    for component in components:
        if not models.Component.query.filter_by(name=component).count():
            db_component = models.Component(name=component,
                                            squad_name=squad_db.name)
            db.session.add(db_component)
    db.session.commit()


def get_DFG_db_object(job):
    DFG = get_DFG_name(job)
    DFG_db = db.DFG.query.filter_by(name=DFG).first()
    return DFG_db


def get_squad_db_object(job):
    squad = get_squad_name(job)
    squad_db = models.Squad.query.filter_by(name=squad).first()
    return squad_db


def get_number_of_jobs(DFG, status=None):
    """Returns the number of jobs of a given DFG."""


def get_DFG_jobs_summary():
    """Returns dictionary of DFGs and their jobs count by status.

    {'network': [<failure_num>, <unstable_num>, <success_num>]}
    """
    summary = {}
    DFGs = [DFG.name for DFG in models.DFG.query.all()]
    for DFG in DFGs:
        pass
        # summary[DFG] = [get_count(DFG=DFG, status=status) for
        #                status in ['failure', 'unstable', 'success']]
    return summary


def load_DFGs():
    """Loads predefined DFGs from file"""
    for DFG, DFG_content in DFGs.items():
        name = get_DFG_name(DFG)
        if not models.DFG.query.filter_by(name=name).count():
            add_dfg_to_db(name)
        for squad, components in DFG_content.items():
            if not models.Squad.query.filter_by(name=squad).count():
                add_squad_to_db(squad, name)
            add_components_to_db(components, squad)
        squad = models.Squad.query.filter_by(name=squad).first()
        for component in components:
            component = models.Component.query.filter_by(
                name=component).first()
            squad.components.append(component)
        db.session.commit()
