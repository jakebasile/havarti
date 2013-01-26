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

from flask import Flask, abort, render_template, redirect, url_for, request
from werkzeug import secure_filename
from datetime import datetime
from havarti.parse import fallback_versions
from havarti.downloader import download_package
from havarti.data import Package, Version, db_session, init_db
import sqlalchemy.orm
import os
import importlib
import base64
import datetime

app = Flask(__name__)

app.config['DEBUG'] = bool(os.environ.get('DEBUG', False))

app.config['PASSCODE'] = os.environ['PASSCODE']

storage = importlib.import_module('.storage.' + os.environ['STORAGE'], package='havarti')

@app.before_first_request
def create_db():
    init_db()

@app.teardown_request
def close_session(excepton=None):
    db_session.remove()

@app.route('/robots.txt')
def robots():
    return 'User-agent: *\nDisallow: /'

@app.route('/i/<package>/')
def get_package(package):
    package = secure_filename(package)
    versions = fallback_versions(package)
    cached_package = Package.query.filter_by(name=package).first()
    if cached_package:
        for fb_version in versions:
            filtered_version = cached_package.versions.filter_by(version_code=fb_version).first()
            if filtered_version == None:
                download_package.delay(package)
                break
        for cached_version in cached_package.versions.all():
            version_url = url_for(
                'get_file',
                package=cached_package.name,
                filename=cached_version.filename,
            )
            versions[cached_version.version_code] = version_url
    else:
        download_package.delay(package)
    return render_template(
        'versions.html',
        versions=versions,
        package_name=package
    )

@app.route('/i/<package>/<filename>')
def get_file(package, filename):
    filename = secure_filename(filename)
    package = secure_filename(package)
    return storage.retrieve_package(package, filename)

@app.route('/u/', methods=['POST'])
def upload():
    print request.headers
    if 'Authorization' not in request.headers:
        abort(403)
    auth = base64.b64decode(request.headers['Authorization'].split()[1]).split(':')
    if auth[0] != 'havarti' or auth[1] != app.config['PASSCODE']:
        abort(403)
    package = secure_filename(request.form['name'])
    cached_package = Package.query.filter_by(name=package).first()
    if request.form[':action'] == 'submit':
        if cached_package == None:
            db_session.add(
                Package(
                    name=package,
                )
            )
            db_session.commit()
            return 'OK'
        else:
            abort(400, 'ALREADY EXISTS')
    elif request.form[':action'] == 'file_upload':
        if cached_package == None:
            cached_package = Package(name=package)
            db_session.add(cached_package)
        elif cached_package.version.filter_by(version_code=request.form['version']).first() != None:
            abort(400, 'ALREADY EXISTS')
        filename = secure_filename(request.files['content'].filename)
        request.files['content'].save(filename)
        storage.store_package(package, filename)
        db_session.add(
            Version(
                version_code=request.form['version'],
                package=cached_package,
                filename=filename,
                date_cached=datetime.datetime.now(),
            )
        )
        db_session.commit()
        os.remove(filename)
        return 'OK'
    else:
        abort(400, 'BAD REQUEST')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run('0.0.0.0', port)
