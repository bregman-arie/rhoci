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
from rhoci.models import DFG


dfg_squads = {'network': {'octavia': ['octavia', 'neutron-lbaas'],
                          'ovn': ['networking-ovn']}
              }


def get_dfg_name(string):
    name = string.split('-')[1]
    if len(name) < 4:
        return name.upper()
    else:
        return name.capitalize()


def dfg_exists(dfg):
    """Returns True if DFG exists in DB else returns False."""
    return (DFG.query.filter_by(name=dfg).count() or
            dfg.lower() == 'dfg')


def add_dfg_to_db(dfg):
    """Inserts DFG into DB."""
    db_dfg = DFG(name=dfg)
    db.session.add(db_dfg)
    db.session.commit()
