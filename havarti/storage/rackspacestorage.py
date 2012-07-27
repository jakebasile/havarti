# Copyright 2012 Jake Basile
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import redirect, abort
import cloudfiles
import pymongo
import os
from uuid import uuid4

def __get_container__(db):
    username = os.environ['RACKSPACE_USERNAME']
    api_key = os.environ['RACKSPACE_KEY']
    conn = cloudfiles.get_connection(username, api_key)
    uuid = db.config.find_one({'name': 'uuid'})
    if not uuid:
        uuid = str(uuid4())
        db.config.insert({'name': 'uuid', 'value': uuid})
    else:
        uuid = uuid['value']
    container_name = 'havarti-' + uuid 
    container = conn.create_container(container_name)
    container.make_public()
    return container

def store_package(db, package, filename):
    obj = __get_container__(db).create_object(package + '/' + filename)
    obj.load_from_filename(filename)

def retrieve_package(db, package, filename):
    try:
        obj = __get_container__(db).get_object(package + '/' + filename)
        return redirect(obj.public_uri())
    except:
        abort(404)

