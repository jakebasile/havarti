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
from flask.ext.pymongo import PyMongo
from werkzeug import secure_filename
from datetime import datetime
from havarti.parse import fallback_versions
from havarti.downloader import download_package
import os
import pymongo
import importlib
import base64

app = Flask(__name__)

app.config['DEBUG'] = bool(os.environ.get('DEBUG', False))

app.config['PASSCODE'] = os.environ['PASSCODE']

mongo_key = os.environ.get('MONGO_KEY', 'LOCAL_MONGO')
if mongo_key == 'LOCAL_MONGO':
    mongo_url = 'mongodb://localhost/havarti'
else:
    mongo_url = os.environ[mongo_key]
mongo_info = pymongo.uri_parser.parse_uri(mongo_url)
app.config['MONGO_HOST'] = mongo_info['nodelist'][0][0]
app.config['MONGO_PORT'] = mongo_info['nodelist'][0][1]
app.config['MONGO_USERNAME'] = mongo_info['username']
app.config['MONGO_PASSWORD'] = mongo_info['password']
app.config['MONGO_DBNAME'] = mongo_info['database']
mongo = PyMongo(app)

storage = importlib.import_module('.storage.' + os.environ['STORAGE'], package='havarti')

def escape_version(version):
    return version.replace('.', '*')

def unescape_version(version):
    return version.replace('*', '.')

@app.route('/robots.txt')
def robots():
    return 'User-agent: *\nDisallow: /'

@app.route('/i/<package>/')
def get_package(package):
    package = secure_filename(package)
    versions = fallback_versions(package)
    cached_package = mongo.db.packages.find_one({'name': package})
    if cached_package:
        for fb_version in versions:
            if escape_version(fb_version) not in cached_package['versions']:
                download_package.delay(package)
                break
        for cached_version in cached_package['versions']:
            version_url = url_for(
                'get_file',
                package=package,
                filename=cached_package['versions'][cached_version]
            )
            versions[unescape_version(cached_version)] = version_url
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
    return storage.retrieve_package(mongo.db, package, filename)

@app.route('/u/', methods=['POST'])
def upload():
    if 'Authorization' not in request.headers:
        abort(403)
    auth = base64.b64decode(request.headers['Authorization'].split()[1]).split(':')
    if auth[0] != 'havarti' or auth[1] != app.config['PASSCODE']:
        abort(403)
    package = secure_filename(request.form['name'])
    if request.form[':action'] == 'submit':
        mongo.db.packages.update(
            {'name': package},
            {
            },
            upsert=True,
        )
        return 'OK'
    elif request.form[':action'] == 'file_upload':
        cached_package = mongo.db.packages.find_one({'name': package})
        if cached_package and escape_version(request.form['version']) in cached_package['versions']:
            abort(400)
        filename = secure_filename(request.files['content'].filename)
        request.files['content'].save(filename)
        storage.store_package(mongo.db, package, filename)
        mongo.db.packages.update(
            {'name': package},
            {
                '$set': {
                    'versions.' + escape_version(request.form['version']): filename,
                },
            },
            upsert=True,
        )
        os.remove(filename)
        return 'OK'
    else:
        abort(400)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run('0.0.0.0', port)
