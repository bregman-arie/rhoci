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
                db.Column('job', db.String(64),
                          db.ForeignKey('job.name')),
                db.Column('build', db.Integer,
                          db.ForeignKey('build.number')),
                )

tests = db.Table('tests',
                 db.Column('test', db.String(64),
                           db.ForeignKey('test.name')),
                 db.Column('build', db.Integer,
                           db.ForeignKey('build.number')),
                 )


class Build(db.Model):
    """Represents Jenkins build."""

    __tablename__ = 'build'

    number = db.Column(db.Integer)
    status = db.Column(db.String(64))
    job_name = db.Column(db.String(64), db.ForeignKey('job.name'))
    jobs = db.relationship('Job', secondary=jobs,
                           backref=db.backref('builds', lazy='dynamic'))
    tests = db.relationship('Test', secondary=jobs,
                            backref=db.backref('builds', lazy='dynamic'))

    def __repr__(self):
        return "<Build number %r\n" % (self.number)
