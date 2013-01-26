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

from havarti.celery import celery
from havarti.parse import fallback_versions
from havarti.data import db_session, Package, Version
import os
import requests
import urlparse
import datetime
import importlib

storage = importlib.import_module('havarti.storage.' + os.environ['STORAGE'])

@celery.task
def download_package(package):
    fb_versions = fallback_versions(package)
    cached_package = Package.query.filter_by(name=package).first()
    if not cached_package:
        cached_package = Package(name=package)
        db_session.add(cached_package)
    for version in fb_versions:
        filtered_version = cached_package.versions.filter_by(version_code=version).first()
        if filtered_version == None:
            filename = urlparse.urlparse(fb_versions[version])[2].split('/')[-1]
            fb_file = requests.get(fb_versions[version]).content
            with open(filename, 'w') as tempfile:
                tempfile.write(fb_file)
            storage.store_package(package, filename)
            db_session.add(
                Version(
                    package=cached_package,
                    version_code=version,
                    filename=filename,
                    date_cached=datetime.datetime.now(),
                )
            )
            os.remove(filename)
    db_session.commit()
    
