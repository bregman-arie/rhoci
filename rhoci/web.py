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
import logging
from logging.handlers import RotatingFileHandler
import os

from rhoci.db.base import db
from rhoci.common.failures import FAILURES
import rhoci.rhosp.DFG as DFG_lib
from rhoci.common import exceptions
from rhoci.filters import configure_template_filters
import rhoci.models as models
import rhoci.views
from rhoci.rhosp.release import RELEASE_MAP
from rhoci.server.config import Config

LOG = logging.getLogger(__name__)
app = Flask(__name__)
configure_template_filters(app)
db.init_app(app)
with app.app_context():
    db.create_all()

from rhoci.agent.jenkins_agent import JenkinsAgent  # noqa

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


class Server(object):
    """RHOCI Server"""

    def __init__(self, args=None):

        self.setup_logging()
        self.load_config(args)

        # If user turned on debug, update logging level
        if app.config['RHOCI_DEBUG']:
            self._update_logging_level(logging.DEBUG)

        self._register_blueprints()
        self._setup_database()
        self._setup_releases()
        self._load_failures()
        self._load_DFGs()
        self._setup_jenkins()

    def _register_blueprints(self):
        """Registers Flask blueprints."""

        for view, prefix in VIEWS:
            app.register_blueprint(view, url_prefix=prefix)

    def load_config(self, args):
        """Load configuration from different sources"""
        app.config.from_object(Config)

        # Check if user pointed to a different config file from CLI or ENV vars
        if vars(args)['RHOCI_CONFIG_FILE']:
            app.config['RHOCI_CONFIG_FILE'] = vars(args)['RHOCI_CONFIG_FILE']
        elif 'RHOCI_CONFIG_FILE' in os.environ:
            app.config['RHOCI_CONFIG_FILE'] = os.environ['RHOCI_CONFIG_FILE']

        self.load_config_from_env()
        self.load_config_from_file()
        self.load_config_from_parser(args)

        # Load DB configuration
        app.config.from_object('rhoci.db.config')
        LOG.info("Loaded configuration:\n + {" + "\n".join("{}: {}".format(
            k, v) for k, v in sorted(app.config.items())) + "}")

        # Make sure critical configuration is provided
        for k in ['JENKINS_URL', 'JENKINS_USER', 'JENKINS_PASSWORD']:
            if not app.config.get('RHOCI_' + k):
                raise exceptions.MissingInputException(parameter='RHOCI_' + k)

    def load_config_from_env(self):
        """Loads configuration from environment variables."""
        rhoci_envs = filter(
            lambda s: s.startswith('RHOCI_'), os.environ.keys())
        for env_key in rhoci_envs:
            if os.environ[env_key]:
                app.config[env_key] = os.environ[env_key]

    def load_config_from_file(self):
        """Loads configuration from a file."""
        cfg_parser = ConfigParser()
        cfg_parser.read(app.config['RHOCI_CONFIG_FILE'])

        for section in cfg_parser.sections():
            for key in cfg_parser.options(section):
                k = "RHOCI_%s_%s" % (section.upper(), key.upper())
                app.config[k] = cfg_parser.get(section, key)

    def load_config_from_parser(self, args):
        """Loads configuration based on provided arguments by the user."""
        for k, v in vars(args).items():
            if v:
                app.config[k] = v

    def _setup_database(self):
        """Sets up the database by setting versioning and creating

        all the tables.
        """
        # setup_versioning(app.config)
        with app.app_context():
            db.create_all()

    def setup_logging(self):
        """Setup logging level and format."""
        format = '[%(asctime)s] %(levelname)s %(module)s: %(message)s'
        level = logging.INFO
        logging.basicConfig(level=level, format=format)
        handler = RotatingFileHandler('rhoci.log', maxBytes=2000000,
                                      backupCount=10)
        logging.getLogger().addHandler(handler)

    def _update_logging_level(self, logging_level):
        """Update logging based on passed level."""

        logging.getLogger().setLevel(logging.DEBUG)

    def run(self):
        """Runs the web server."""
        LOG.info("Running rhoci web server")

        app.run(threaded=True, host='0.0.0.0', port=int(
            app.config['RHOCI_SERVER_PORT']))

    def _load_DFGs(self):
        """Loads RHOSP DFGs.

        Note: it doesn't load full list as the app discovers them when parsing
              data from Jenkins. The reason it loads some of them is because
              we associate some of them with squads and components which
              can't be done by Jenkins
        """
        for dfg, dfg_data in DFG_lib.DFGs.iteritems():
            name = DFG_lib.get_DFG_name(dfg)
            with app.app_context():
                if not models.DFG.query.filter_by(name=name).count():
                    DFG_lib.add_dfg_to_db(name)
                for squad, components in dfg_data.iteritems():
                    if not models.Squad.query.filter_by(name=squad).count():
                        DFG_lib.add_squad_to_db(squad, name)
                    DFG_lib.add_components_to_db(components, squad)
                squad = models.Squad.query.filter_by(name=squad).first()
                for component in components:
                    component = models.Component.query.filter_by(
                        name=component).first()
                    squad.components.append(component)
                db.session.commit()
            LOG.debug("Loaded DFGs, squads and components")

    def _load_failures(self):
        """Loads RHOCI built-in failure to DB."""
        for f in FAILURES:
            with app.app_context():
                if not models.Failure.query.filter_by(name=f['name']).count():
                    failure_db = models.Failure(category=f['category'],
                                                pattern=f['pattern'],
                                                name=f['name'],
                                                upper_bound_pattern=f[
                                                    'upper_bound_pattern'],
                                                lower_bound_pattern=f[
                                                    'lower_bound_pattern'],
                                                action=f['action'],
                                                cause=f['cause'])
                    db.session.add(failure_db)
                    db.session.commit()
                    logging.info("Loaded a new failure: %s" % f['name'])

    def _setup_releases(self):
        """Create DB entry for each release."""
        for release in app.config['RHOCI_RELEASES'].split(','):
            with app.app_context():
                if not models.Release.query.filter_by(
                        number=release).count():
                    release_db = models.Release(
                        number=release, name=RELEASE_MAP[release])
                    db.session.add(release_db)
                    db.session.commit()
                    logging.info("Added release %s to the DB" % release)

    def _setup_jenkins(self):
        """Create Jenkins agent to pull information from RHOSP Jenkins."""
        agent = JenkinsAgent(name="RHOSP",
                             user=app.config.get('RHOCI_JENKINS_USER'),
                             password=app.config.get('RHOCI_JENKINS_PASSWORD'),
                             url=app.config.get('RHOCI_JENKINS_URL'),
                             app=app)
        logging.debug("Starting connection to RHOSP Jenkins")
        agent.pre_run_process.start()
        agent.run_process.start()
