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

from flask import abort, current_app, request 
from gridfs import GridFS, NoFile
from werkzeug.wsgi import wrap_file
from mimetypes import guess_type

cache_for=31536000

def get_package_filename(package, filename):
    return '/' + package + '/' + filename 

def store_package(db, package, filename):
    storage = GridFS(db, 'fs')
    file = open(filename, 'r')
    storage.put(
        file.read(),
        filename=get_package_filename(package, filename),
    )

def retrieve_package(db, package, filename):
    storage = GridFS(db, 'fs')
    try:
        fileobj = storage.get_last_version(filename=get_package_filename(package, filename))
    except NoFile:
        abort(404)

    data = wrap_file(request.environ, fileobj, buffer_size=1024 * 256)
    response = current_app.response_class(
        data,
        mimetype=guess_type(fileobj.filename)[0],
        direct_passthrough=True
    )
    response.content_length = fileobj.length
    response.last_modified = fileobj.upload_date
    response.set_etag(fileobj.md5)
    response.cache_control.max_age = cache_for
    response.cache_control.s_max_age = cache_for
    response.cache_control.public = True
    response.make_conditional(request)
    return response
