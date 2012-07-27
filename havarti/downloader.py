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

from havarti.celery import celery
from havarti.parse import fallback_versions
import os
import requests
import urlparse
import pymongo
import importlib

storage = importlib.import_module('havarti.storage.' + os.environ['STORAGE'])

mongo_key = os.environ.get('MONGO_KEY', 'LOCAL_MONGO')
if mongo_key == 'LOCAL_MONGO':
    mongo_url = 'mongodb://localhost/havarti'
else:
    mongo_url = os.environ[mongo_key]
mongo_info = pymongo.uri_parser.parse_uri(mongo_url)
db = pymongo.Connection(mongo_url)[mongo_info['database']]

def escape_version(version):
    return version.replace('.', '*')

@celery.task
def download_package(package):
    fb_versions = fallback_versions(package)
    cached_package = db.packages.find_one({'name': package})
    for version in fb_versions:
        if not cached_package or escape_version(version) not in cached_package['versions']:
            filename = urlparse.urlparse(fb_versions[version])[2].split('/')[-1]
            fb_file = requests.get(fb_versions[version]).content
            with open(filename, 'w') as tempfile:
                tempfile.write(fb_file)
            storage.store_package(db, package, filename)
            db.packages.update(
                {'name': package},
                {
                    '$set': {
                        'versions.' + escape_version(version): filename,
                    },
                },
                upsert=True
            )
            os.remove(filename)
    
