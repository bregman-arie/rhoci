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
from flask import Flask
import logging
import os
import yaml

from rhoci import log
from rhoci.db.base import db
import rhoci.rhosp.DFG as DFG_lib
from rhoci.filters import configure_template_filters
from rhoci.views.consts import VIEWS
from rhoci.server.config import Config

LOG = logging.getLogger(__name__)

app = Flask(__name__)
configure_template_filters(app)
db.init_app(app)
with app.app_context():
    db.create_all()

from rhoci.jenkins import agent  # noqa


class Server(object):
    """Application Server"""

    def __init__(self, args=None):

        log.setup_logging()
        self.load_config(args)
        if args.debug:
            log._update_logging_level(logging.DEBUG)
        self._register_blueprints()
        self._setup_database()
        self._load_predefined_data()
        self._run_jenkins_agent()

    def _load_predefined_data(self):
        """Load predefined data the app was installed with."""
        with app.app_context():
            DFG_lib.load_DFGs()

    def _register_blueprints(self):
        """Registers Flask blueprints."""

        for view, prefix in VIEWS:
            app.register_blueprint(view, url_prefix=prefix)

    def load_config(self, args):
        """Load configuration from different sources"""
        # Load built-in default configuration
        app.config.from_object(Config)
        # Check if user pointed to non-default configuration file
        if vars(args)['config_file']:
            app.config['config_file'] = vars(args)['config_file']
        elif 'RHOCI_CONFIG_FILE' in os.environ:
            app.config['config_file'] = os.environ['RHOCI_CONFIG_FILE']

        self.load_config_from_file()
        self.load_config_from_parser(args)

        # Load DB configuration
        app.config.from_object('rhoci.db.config')
        LOG.debug("Loaded configuration:\n + {" + "\n".join("{}: {}".format(
            k, v) for k, v in sorted(app.config.items())) + "}")

    def load_config_from_file(self):
        """Loads configuration from a file."""
        with open(app.config['config_file'], 'r') as f:
            data = yaml.load(f)
            for k, v in data.items():
                app.config[k] = v

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

    def run(self):
        """Runs the web server."""
        LOG.info("Running rhoci web server")

        app.run(threaded=True, host='0.0.0.0', port=int(app.config['RHOCI_SERVER_PORT']))

    def _run_jenkins_agent(self):
        """Create and execute Jenkins agent."""
        jenkins_agent = agent.Jenkins(user=app.config.get('jenkins')['user'],
                                      password=app.config.get('jenkins')['password'],
                                      url=app.config.get('jenkins')['url'],
                                      app=app)
        LOG.debug("Starting connection to Jenkins")
        jenkins_agent.pre_run_process.start()
        jenkins_agent.run_process.start()
