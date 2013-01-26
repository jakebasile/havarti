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
import os

def __get_bucket__():
    s3 = boto.connect_s3(os.environ['S3_ACCESS_KEY'], os.environ['S3_SECRET_KEY'])
    bucket = s3.create_bucket(os.environ['S3_BUCKET'])
    return bucket

def store_package(package, filename):
    key = __get_bucket__().new_key(package + '/' + filename)
    key.set_contents_from_filename(filename)

def retrieve_package(package, filename):
    key = __get_bucket__().get_key(package + '/' + filename)
    if key:
        return redirect(key.generate_url(3600))
    else:
        return abort(404)

