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

import bs4
import requests
import urlparse
import os
import re

fallback_uri = os.environ.get(
    'FALLBACK',
    'http://pypi.python.org/simple/'
)

def fallback_versions(package):
    base_url = urlparse.urljoin(fallback_uri, package)
    try:
        fb_response = requests.get(base_url, timeout=5)
    except:
        return {}
    base_url = fb_response.url
    soup = bs4.BeautifulSoup(fb_response.text)
    versions = {}
    version_re = re.compile(
        '^.*%s-(.*)\\.(tar|tar\\.gz|tgz|tar\\.bz2|zip|pybundle)/?$' % package,
        re.IGNORECASE
    )
    for link in soup.find_all('a'):
        href = link.get('href')
        path = urlparse.urlparse(href)[2]
        match = version_re.match(path)
        if match:
            versiontext = match.group(1)
            versions[versiontext] = urlparse.urljoin(base_url, href)
    return versions
