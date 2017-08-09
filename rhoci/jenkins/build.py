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


def get_last_build_number(job_info):
    """Given a job info dict, returns the last build number."""
    if job_info['lastCompletedBuild']:
        return job_info['lastCompletedBuild']['number']
    else:
        return 0


def get_build_result(conn, job_name, build_number):
    """Given a Jenkins connection and job name, it returns string of

    the last completed build result.
    """
    return str(conn.get_build_info(job_name, build_number)['result'])


def get_console_output(conn, job_name, build_number=None):
    """Return console output of a given build."""
    build = build_number or get_last_build_number(
        conn.get_job_info(job_name))
    print conn.get_job_info(job_name)
    # return (conn.get_build_console_output(job_name, build)).encode('utf-8')
