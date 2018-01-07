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
from rhoci.models import Bug
from rhoci.models import Job
from rhoci.models import Test
from rhoci.db.base import db

import logging

LOG = logging.getLogger(__name__)


def add_bug(number, summary, status, system):
    """Adds a given bug to the DB."""
    bug = Bug(number=int(number), summary=summary, status=status,
              system=system)
    db.session.add(bug)
    db.session.commit()


def remove_from_all(number):
    """Removes bug entirely."""
    bug = Bug.query.filter_by(number=number).first()
    db.session.delete(bug)
    db.session.commit()


def remove_from_job(bug_num, job_name):
    """Removes bug from the given job."""
    bug = Bug.query.filter_by(number=bug_num).first()
    job = Job.query.filter_by(name=job_name).first()
    job.bugs.remove(bug)
    db.session.commit()


def remove_from_test(bug_num, test_class, test_name):
    """Unlinks between a test and a bug."""
    bug = Bug.query.filter_by(number=bug_num).first()
    test = Test.query.filter_by(class_name=test_class,
                                test_name=test_name).first()
    test.bugs.remove(bug)
    db.session.commit()
