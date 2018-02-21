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
from datetime import datetime

from rhoci.db.base import db


# Association tables
# bugs <-> jobs
bugs = db.Table('bugs',
                db.Column('bug_id', db.Integer, db.ForeignKey('bug.id'),
                          primary_key=True),
                db.Column('job_id', db.Integer, db.ForeignKey('job.id'),
                          primary_key=True))

# jobs <-> builds
builds = db.Table('builds',
                  db.Column('build_id', db.Integer, db.ForeignKey('build.id'),
                            primary_key=True),
                  db.Column('job_id', db.Integer, db.ForeignKey('job.id'),
                            primary_key=True))

bugs_tests = db.Table('bugs_tests',
                      db.Column('bug_id', db.Integer, db.ForeignKey('bug.id'),
                                primary_key=True),
                      db.Column('test_id', db.Integer,
                                db.ForeignKey('test.id'), primary_key=True))


class Agent(db.Model):
    """Represents agent of an external system."""

    __tablename__ = 'agent'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    url = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))
    user = db.Column(db.String(64))
    active = db.Column(db.Boolean)
    update_time = db.Column(db.DateTime)

    @property
    def serialize(self):
        """Return serialized agent object."""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'user': self.user,
            'active': self.active,
            'update_time': self.update_time,
        }


class Build(db.Model):
    """Represents build."""

    __tablename__ = 'build'

    id = db.Column(db.Integer)
    job = db.Column(db.String(64), primary_key=True)
    number = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean)
    status = db.Column(db.String(64))
    url = db.Column(db.String(128))
    trigger = db.Column(db.String(128))
    parameters = db.Column(db.Text)
    failure_text = db.Column(db.Text)
    failure_name = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def serialize(self):
        """Return build object data in serializeable format"""
        return {
            'id': self.id,
            'job': self.job,
            'number': self.number,
            'active': self.active,
            'status': self.status,
            'url': self.url,
            'timestamp': self.timestamp,
            'trigger': self.trigger,
            'parameters': eval(self.parameters) if self.parameters else {},
            'failure_text': self.failure_text,
            'failure_name': self.failure_name,
        }


class Job(db.Model):
    """Represents Jenkins job."""

    __tablename__ = 'job'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    last_build_number = db.Column(db.Integer)
    last_build_result = db.Column(db.String(64))
    job_type = db.Column(db.String(64))
    release_number = db.Column(db.Integer, db.ForeignKey('release.number'))
    release = db.relationship("Release", uselist=False, backref="release")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    builds = db.relationship('Build', secondary=builds, lazy='subquery',
                             backref=db.backref('jobs', lazy=True))
    bugs = db.relationship('Bug', secondary=bugs, lazy='subquery',
                           backref=db.backref('jobs', lazy=True))

    @property
    def serialize(self):
        """Return serialized Job."""
        return {
            'id': self.id,
            'name': self.name,
            'last_build_number': self.last_build_number,
            'last_build_result': self.last_build_result,
            'job_type': self.job_type,
            'timestamp': self.timestamp,
            'bugs': self.serialize_bugs,
            'builds': self.serialize_builds,
        }

    @property
    def serialize_bugs(self):
        return [item.serialize for item in self.bugs]

    @property
    def serialize_builds(self):
        return [item.serialize for item in self.builds]

    def __repr__(self):
        return self.serialize()


class Test(db.Model):
    """Represents a single unique test."""

    __tablename__ = 'test'

    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(128))
    test_name = db.Column(db.String(128))
    failure = db.Column(db.Integer)
    success = db.Column(db.Integer)
    skipped = db.Column(db.Integer)
    bugs = db.relationship('Bug', secondary=bugs_tests, lazy='subquery',
                           backref=db.backref('tests', lazy=True))

    @property
    def serialize(self):
        """Return test object data in serializeable format"""
        return {
            'class_name': self.class_name,
            'test_name': self.test_name,
            'failure': self.failure,
            'skipped': self.skipped,
            'success': self.success,
            'bugs': self.serialize_bugs,
        }

    @property
    def serialize_bugs(self):
        return [item.serialize for item in self.bugs]


class TestBuild(db.Model):
    """Represents a test in a context of build."""

    __tablename__ = 'test_build'

    id = db.Column(db.Integer)
    class_name = db.Column(db.String(128), primary_key=True)
    job = db.Column(db.String(64), primary_key=True)
    build = db.Column(db.String(64), primary_key=True)
    status = db.Column(db.String(64))
    skipped = db.Column(db.String(64))
    name = db.Column(db.String(64), primary_key=True)
    duration = db.Column(db.String(64))
    errorStackTrace = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def serialize(self):
        """Return serialized test build object."""
        return {
            'class_name': self.class_name,
            'job': self.job,
            'build': self.build,
            'status': self.status,
            'skipped': self.skipped,
            'name': self.name,
            'duration': self.duration,
            'errorStackTrace': self.errorStackTrace
        }


class Node(db.Model):
    """Represents node."""

    __tablename__ = 'node'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)

    @property
    def serialize(self):
        """Return serialized Node object."""
        return {'number': self.name}


class Release(db.Model):
    """Represents RHOSP release."""

    __tablename__ = 'release'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, index=True, unique=True)
    name = db.Column(db.String(64), unique=True)

    @property
    def serialize(self):
        """Return serialized Release object."""
        return {'number': self.number}


class Plugin(db.Model):
    """Represents Jenkins plugin."""

    __tablename__ = 'plugin'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)

    @property
    def serialize(self):
        """Return serialized Plugin object"""
        return {'name': self.name}


class DFG(db.Model):
    """Represents DFG."""

    __tablename__ = 'DFG'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    squads = db.relationship('Squad', backref='DFG', lazy=True)

    @property
    def serialize(self):
        """Return serialized DFG object"""
        return {'name': self.name,
                'squads': self.serialize_squads}

    @property
    def serialize_squads(self):
        return [item.serialize for item in self.squads]


class Squad(db.Model):
    """Represents Squad."""

    __tablename__ = 'squad'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    DFG_name = db.Column(db.String(64), db.ForeignKey('DFG.name'),
                         nullable=False)
    components = db.relationship('Component', backref="squad", lazy='dynamic')

    @property
    def serialize(self):
        """Return serialized squad object"""
        return {self.name: self.serialize_components}

    @property
    def serialize_components(self):
        return [item.serialize for item in self.components]


class Component(db.Model):
    """Represents OpenStack Component."""

    __tablename__ = 'component'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    squad_name = db.Column(db.String(64), db.ForeignKey('squad.name'),
                           nullable=False)

    @property
    def serialize(self):
        """Return serialized component object"""
        return {'component': self.name}


class Artifact(db.Model):
    """Represents an artifact"""

    __tablename__ = 'artifact'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    relativePath = db.Column(db.String(128))
    build = db.Column(db.Integer)
    job = db.Column(db.String(64))


class Failure(db.Model):
    """Represents a failure of build"""

    __tablename__ = 'failure'

    id = db.Column(db.Integer)
    name = db.Column(db.String(128), primary_key=True)
    pattern = db.Column(db.String(128))
    upper_bound_pattern = db.Column(db.String(128))
    lower_bound_pattern = db.Column(db.String(128))
    category = db.Column(db.String(128))
    action = db.Column(db.String(128))
    cause = db.Column(db.String(128))

    @property
    def serialize(self):
        """Return test object data in serializeable format"""
        return {
            'name': self.name,
            'pattern': self.pattern,
            'upper_bound_pattern': self.upper_bound_pattern,
            'lower_bound_pattern': self.lower_bound_pattern,
            'category': self.category,
            'action': self.action,
            'cause': self.cause,
        }


class Bug(db.Model):
    """Represents a bug"""

    __tablename__ = 'bug'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    summary = db.Column(db.String(128), unique=True)
    system = db.Column(db.String(128))
    status = db.Column(db.String(32))
    assigned_to = db.Column(db.String(128))

    @property
    def serialize(self):
        """Return serialized object of Bug model."""
        return {
            'id': self.id,
            'number': self.number,
            'summary': self.summary,
            'system': self.system,
            'status': self.status,
            'assigned_to': self.assigned_to,
        }
