# Copyright 2012-2013 Jake Basile and Contributors
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
import boto
import pymongo
from uuid import uuid4

def __get_bucket__(db):
    s3 = boto.connect_s3()
    uuid = db.config.find_one({'name': 'uuid'})
    if not uuid:
        uuid = str(uuid4())
        db.config.insert({'name': 'uuid', 'value': uuid})
    else:
        uuid = uuid['value']
    bucket_name = 'havarti-' + uuid 
    bucket = s3.create_bucket(bucket_name)
    return bucket

def store_package(db, package, filename):
    key = __get_bucket__(db).new_key(package + '/' + filename)
    key.set_contents_from_filename(filename)

def retrieve_package(db, package, filename):
    key = __get_bucket__(db).get_key(package + '/' + filename)
    if key:
        return redirect(key.generate_url(3600))
    else:
        return abort(404)

