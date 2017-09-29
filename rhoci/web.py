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
from configparser import ConfigParser
from flask import Flask
from gevent.pywsgi import WSGIServer
import logging
import os

from rhoci.views.doc import auto
from rhoci.db.base import db
from rhoci.filters import configure_template_filters
import rhoci.models as models
import rhoci.views
from rhoci.rhosp.release import RELEASE_MAP

logger = logging.getLogger(__name__)
app = Flask(__name__)
configure_template_filters(app)
db.init_app(app)
with app.app_context():
    db.create_all()

import rhoci.agent.jenkins_agent as j_agent  # noqa

views = (
    (rhoci.views.home, ''),
    (rhoci.views.jobs, '/jobs'),
    (rhoci.views.doc, '/doc'),
    (rhoci.views.builds, '/builds'),
    (rhoci.views.nodes, '/nodes'),
    (rhoci.views.jenkins_notifications, '/jenkins_notifications'),
    (rhoci.views.plugins, '/plugins'),
    (rhoci.views.add_job, '/add_job'),
    (rhoci.views.job_analyzer, '/job_analyzer'),
    (rhoci.views.review_statistics, '/review_statistics'),
)


class WebApp(object):
    """rhoci Web Application."""

    DEFAULT_BIND_HOST = '0.0.0.0'
    DEFAULT_PORT = 5000
    DEFAULT_CONFIG_FILE = '/etc/rhoci/rhoci.conf'

    def __init__(self, args_ns):

        self._setup_logging()
        self._setup_config(args_ns)

        # If user turned on debug, update logging level
        if self.config['DEBUG']:
            self._update_logging_level(logging.DEBUG)

        # Initialize API documentation
        auto.init_app(app)

        self._register_blueprints()
        self._setup_database()
        self._setup_releases()
        self._setup_jenkins()

    def _register_blueprints(self):
        """Registers Flask blueprints."""

        for view, prefix in views:
            app.register_blueprint(view, url_prefix=prefix)

    def _setup_config(self, args_ns):
        """Load configuration from file"""

        self.config = self._load_config_from_cli(args_ns)
        config_f = vars(args_ns)['config_file'] or self.DEFAULT_CONFIG_FILE

        # If configuration file exists, load it and update the app config
        if os.path.exists(config_f):
            self._load_config_from_file(config_f)
        app.config.update(self.config)

        # Load DB configuration
        app.config.from_object('rhoci.db.config')

    def _setup_database(self):
        """Sets up the database by setting versioning and creating

        all the tables.
        """
        # setup_versioning(app.config)
        with app.app_context():
            db.create_all()

    def _load_config_from_cli(self, args_ns):
        """Load arguments as passed by the user.

        returns dictionary of configartion options and their values.
        """
        config = {}

        # Convert Namespace instance into a dictionary of args:values
        # so we can load them into Flask configuration
        for k, v in vars(args_ns).iteritems():
            config[k.upper()] = v

        return config

    def _load_config_from_file(self, config_f):
        """Loads configuration from file."""
        parser = ConfigParser()
        parser.read(config_f)

        for section in parser.sections():
                for option in parser.options(section):
                    self.config[option] = parser.get(section, option)
        logger.info("Updated config from file: %s" % config_f)
        logger.info("Configuration: %s" % self.config)

    def _setup_logging(self):
        """Setup logging level."""

        format = '%(levelname)s: %(name)s | %(message)s'
        level = logging.INFO
        logging.basicConfig(level=level, format=format)

    def _update_logging_level(self, logging_level):
        """Update logging based on passed level."""

        logging.getLogger().setLevel(logging.DEBUG)

    def run(self):
        """Runs the web server."""
        logger.info("Running rhoci web server")

        listen_socket = (
            app.config.get('BIND_HOST', self.DEFAULT_BIND_HOST),
            app.config.get('PORT', self.DEFAULT_PORT)
        )

        self.server = WSGIServer(listen_socket,
                                 application=app,
                                 log='default')
        self.server.serve_forever()

    def _setup_releases(self):
        """Create DB entry for each release."""
        for release in app.config['releases'].split(','):
            with app.app_context():
                print models
                if not models.Release.query.filter_by(
                        number=release).count():
                    release_db = models.Release(
                        number=release, name=RELEASE_MAP[release])
                    db.session.add(release_db)
                    db.session.commit()
                    logging.info("Added release %s to the DB" % release)

    def _setup_jenkins(self):
        """Create Jenkins agent to pull information from RHOSP Jenkins."""
        agent = j_agent.JenkinsAgent(name="RHOSP",
                                     user=app.config.get('user'),
                                     password=app.config.get('password'),
                                     url=app.config.get('url'),
                                     app=app)
        logging.debug("Starting connection to RHOSP Jenkins")
        agent.pre_run_process.start()
        agent.run_process.start()
