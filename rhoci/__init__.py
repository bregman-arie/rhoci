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

from rhoci.database import Database

from flask import Flask


def create_app():
    # Create application
    app = Flask(__name__)

    Database.initialize()

    register_blueprints(app)

    return app


def register_blueprints(app):

    from rhoci.main import bp as main_bp
    app.register_blueprint(main_bp)
