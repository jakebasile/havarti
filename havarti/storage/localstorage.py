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

from flask import abort, send_file
import os
import shutil

package_cache = os.environ.get('PACKAGE_CACHE', '~/.havarti-packages/')

def get_package_filename(package, filename):
    pkgs_dir = os.path.expanduser(package_cache)
    if not os.path.exists(pkgs_dir):
        os.makedirs(pkgs_dir)
    pkg_dir = os.path.join(pkgs_dir, package)
    if not os.path.exists(pkg_dir):
        os.makedirs(pkg_dir)
    return os.path.join(pkg_dir, filename)

def store_package(db, package, filename):
    shutil.copyfile(filename, get_package_filename(package, filename))

def retrieve_package(db, package, filename):
    pkg_filename = get_package_filename(package, filename)
    if os.path.exists(pkg_filename):
        return send_file(pkg_filename)
    else:
        abort(404)
