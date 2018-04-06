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
from rhoci import models


DFGs = {'network': {
    'vNES': ['neutron', 'python-neutronclient'],
    'Octavia': ['octavia', 'neutron-lbaas'],
    'OVN': ['networking-ovn']}}


def get_dfg_name(string):
    """
    Gets string like 'DFG-network-neutron-12'

    Returns DFG name. In the example above: Network.
    """
    name = string.split('-')[1] if '-' in string else string
    print name
    return name.upper() if len(name) < 4 else name.capitalize()


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
        db_component = models.Component(name=component,
                                        squad_name=squad_db.name)
        db.session.add(db_component)
    db.session.commit()
