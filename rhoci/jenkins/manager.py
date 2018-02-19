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
import logging

from rhoci.jenkins import build
from rhoci.jenkins import job

LOG = logging.getLogger(__name__)


def update_db(data):
    """Update DB with information recieved from Jenkins.

    Returns string to indicate if update was successful or not
    """
    try:
        if not db.session.query(Job).filter_by(name=data['name']).scalar():
            job.update_in_db(data)
        build.update_in_db(data)
        return "Updated DB"
    except Exception as e:
        LOG.error(
            "Was unable to update the DB with the new data: %s" % e.message)
