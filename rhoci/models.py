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


class Agent(db.Model):
    """Represents Jenkins agent/connection."""

    __tablename__ = 'agent'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    url = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))
    user = db.Column(db.String(64))
    number_of_jobs = db.Column(db.Integer)
    number_of_nodes = db.Column(db.Integer)
    number_of_plugins = db.Column(db.Integer)
    active = db.Column(db.Boolean)
    update_time = db.Column(db.DateTime)

    def __repr__(self):
        return "<Agent %r\nNumber of jobs: %s\nNumber of \
nodes: %s\nNumber of plugins: %s\nLast update: %s" % (self.name,
                                                      self.number_of_jobs,
                                                      self.number_of_nodes,
                                                      self.number_of_plugins,
                                                      self.update_time)


class Build(db.Model):
    """Represents Jenkins build."""

    __tablename__ = 'build'

    id = db.Column(db.Integer)
    job = db.Column(db.String(64), primary_key=True)
    number = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean)
    status = db.Column(db.String(64))
    url = db.Column(db.String(128))
    trigger = db.Column(db.String(128))
    parameters = db.Column(db.Text)

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
            'trigger': self.trigger,
            'parameters': eval(self.parameters) if self.parameters else {},
        }


class Job(db.Model):
    """Represents Jenkins job."""

    __tablename__ = 'job'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    jenkins_server = db.Column(db.String(64))
    last_build_number = db.Column(db.Integer)
    last_build_status = db.Column(db.String(64))
    job_type = db.Column(db.String(64))
    release_number = db.Column(db.Integer, db.ForeignKey('release.number'))
    release = db.relationship("Release", uselist=False, backref="release")

    @property
    def serialize(self):
        """Return job object data in serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'last_build_number': self.last_build_number,
            'last_build_status': self.last_build_status,
            'job_type': self.job_type,
        }

    def __repr__(self):
        return self.serialize()


class Test(db.Model):
    """Represents a single unique test."""

    __tablename__ = 'test'

    id = db.Column(db.Integer)
    class_name = db.Column(db.String(128), primary_key=True)
    failure = db.Column(db.Integer)
    success = db.Column(db.Integer)

    @property
    def serialize(self):
        """Return test object data in serializeable format"""
        return {
            'class_name': self.class_name,
            'failure': self.failure,
            'success': self.success
        }


class TestBuild(db.Model):
    """Represents a test in a context of build."""

    __tablename__ = 'test_build'

    id = db.Column(db.Integer)
    class_name = db.Column(db.String(128), primary_key=True)
    job = db.Column(db.String(64), primary_key=True)
    build = db.Column(db.String(64), primary_key=True)
    status = db.Column(db.String(64))
    skipped = db.Column(db.String(64))
    name = db.Column(db.String(64))
    duration = db.Column(db.String(64))
    errorStackTrace = db.Column(db.Text)

    @property
    def serialize(self):
        """Return test build object data in serializeable format"""
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
    """Represents Jenkins node."""

    __tablename__ = 'node'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)

    def __repr__(self):
        return "<Node %r" % (self.name)


class Release(db.Model):
    """Represents RHOSP release."""

    __tablename__ = 'release'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String, index=True, unique=True)
    name = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return "<Release %r" % (self.name)


class Plugin(db.Model):
    """Represents Jenkins plugin."""

    __tablename__ = 'plugin'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)

    def __repr__(self):
        return "<Plugin %r" % (self.name)


class DFG(db.Model):
    """Represents DFG."""

    __tablename__ = 'DFG'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    @property
    def serialize(self):
        """Return DFG object data in serializeable format"""
        return {
            'name': self.name,
        }


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
