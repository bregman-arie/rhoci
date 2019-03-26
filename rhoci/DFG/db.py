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
from __future__ import absolute_import

import logging

from rhoci.models.DFG import DFG as DFG_db

LOG = logging.getLogger(__name__)


def insert_DFG_data_to_db(DFGs):
    """Iterates over a list of DFGs and inserts their data into the db."""
    for DFG in DFGs:
        new_DFG = DFG_db(
            name=DFG['name'],
            squads=[sqd['name'] for sqd in DFG['squads']],
            components=[
                comp for sqd in DFG['squads'] for comp in sqd['components']],
            squad_to_components={
                sqd['name']: sqd['components'] for sqd in DFG['squads']})
        new_DFG.insert()
