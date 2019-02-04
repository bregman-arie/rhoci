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
import rhoci.views

VIEWS = (
    (rhoci.views.home, ''),
    (rhoci.views.jobs, '/jobs'),
    (rhoci.views.doc, '/doc'),
    (rhoci.views.builds, '/builds'),
    (rhoci.views.tests, '/tests'),
    (rhoci.views.nodes, '/nodes'),
    (rhoci.views.plugins, '/plugins'),
    (rhoci.views.dfg, '/dfg'),
    (rhoci.views.add_job, '/add_job'),
    (rhoci.views.job_analyzer, '/job_analyzer'),
    (rhoci.views.review_statistics, '/review_statistics'),
)
