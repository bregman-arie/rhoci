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


class Test(db.Model):
    """Represents Test."""

    __tablename__ = 'test'

    name = db.Column(db.String(64))
    result = db.Column(db.String(64))

    def __repr__(self):
        return "<Test %s\nresult: %s" % (self.name,
                                         self.result)
