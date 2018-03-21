# Copyright 2018 Arie Bregman
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
import datetime


def convert_unixtime_to_datetime(unixtime):
    """Converts unix time to datetime and returns it

    Example:
        1521639729788 -> Wed, Mar 21, 2018
    """
    return datetime.datetime.fromtimestamp(int(unixtime / 1000))
