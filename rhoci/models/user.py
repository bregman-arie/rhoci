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

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from rhoci.database import Database


class User(object):

    def __init__(self, username):
        self.username = username

    @staticmethod
    def is_authenticated():
        return True

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username

    @staticmethod
    def check_password(password_hash, password):
        return check_password_hash(password_hash, password)

    @classmethod
    def find_one(cls, username):
        """Returns one query result."""
        query = {}
        if username:
            query['username'] = username
        user = Database.find_one(collection="users", query=query)
        return user

    def insert(self):
        """Inserts object to the database."""
        if not Database.find_one("users", {"username": self.username}):
            Database.insert(collection='users',
                            data=self.json())

    def json(self):
        return {
            'username': self.username,
            'password': self.password_hash,
        }
