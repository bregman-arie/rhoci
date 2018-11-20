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
import logging
from logging.handlers import RotatingFileHandler

LOG = logging.getLogger(__name__)
MAX_LOG_SIZE = 2000000
LOG_ROTATION_COUNT = 10


def setup_logging(app_name):
    """Setup logging level and format."""
    format = '[%(asctime)s] %(levelname)s %(module)s: %(message)s'
    level = logging.INFO
    logging.basicConfig(level=level, format=format)
    handler = RotatingFileHandler("%s.log" % app_name.lower(),
                                  maxBytes=MAX_LOG_SIZE,
                                  backupCount=LOG_ROTATION_COUNT)
    logging.getLogger().addHandler(handler)


def _update_logging_level(logging_level):
    """Update logging based on passed level."""

    logging.getLogger().setLevel(logging.DEBUG)
