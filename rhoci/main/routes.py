# Copyright 2019 Arie Bregman
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

from flask import render_template
import logging

from rhoci.models.build import Build
from rhoci.models.job import Job
from rhoci.models.DFG import DFG
import rhoci.jenkins.constants as jenkins_const

LOG = logging.getLogger(__name__)

from rhoci.main import bp  # noqa


def get_DFGs_result_summary(DFGs):
    """Given a list of DFG names, returns a dictionary with the
    summary of a given DFG CI jobs.
    DFGs_summary = {'Network': {'FAILED': 2,
                                'PASSED': 12},
                    'Compute': {'FAILED': 3,
                    ...
                   }
    """
    DFGs_summary = dict()
    for DFG_name in DFGs:
        DFGs_summary[DFG] = {}
        for res in jenkins_const.RESULTS:
            DFGs_summary[DFG_name][res] = Job.count(
                name_regex='DFG-{}'.format(DFG_name),
                last_build_res=res)
    return DFGs_summary


@bp.route('/')
def index():
    """Main page route."""
    overall_status = dict()
    count = dict()
    count['jobs'] = Job.count()
    count['DFGs'] = DFG.count()
    count['builds'] = Build.count()
    builds_count_li, dates_li = Build.get_builds_count_per_date()
    for res in jenkins_const.RESULTS:
        overall_status[res] = Job.count(last_build_res=res)
    return render_template('main/index.html', count=count,
                           overall_status=overall_status,
                           builds_count_li=list(reversed((builds_count_li))),
                           dates_li=list(reversed(dates_li)))
