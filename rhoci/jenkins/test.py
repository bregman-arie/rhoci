# Copyright 2018 Arie Bregman
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

from rhoci.db.base import db
import rhoci.models as models

LOG = logging.getLogger(__name__)


def add_bug(class_name, test_name, bug_num):
    """Links between a given test and a bug."""
    test_db = models.Test.query.filter_by(class_name=class_name,
                                          test_name=test_name).first()
    bug_db = models.Bug.query.filter_by(number=bug_num).first()
    test_db.bugs.append(bug_db)
    db.session.commit()
