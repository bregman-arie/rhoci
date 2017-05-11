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

jobs = db.Table('jobs',
                db.Column('parent_job', db.String(64),
                          db.ForeignKey('job.name')),
                db.Column('sub_job', db.String(64),
                          db.ForeignKey('job.name')),
                )


class Job(db.Model):
    """Represents Jenkins job."""

    __tablename__ = 'job'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    jenkins_server = db.Column(db.String(64))
    last_build_number = db.Column(db.Integer)
    last_build_result = db.Column(db.String(64))
    job_type = db.Column(db.String(64))
    release_number = db.Column(db.Integer, db.ForeignKey('release.number'))
    release = db.relationship("Release", uselist=False, backref="release")

    def is_sub_job(self, job):
        return self.sub_jobs.filter(
            jobs.c.sub_job == job.name).count() > 0

    def add_sub_job(self, job):
        if not self.is_sub_job(job):
            self.sub_jobs.append(job)
            return self

    def __repr__(self):
        return "<Job %r\nJob Type: %s" % (self.name, self.job_type)
