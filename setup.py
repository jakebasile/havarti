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

from setuptools import setup, find_packages

setup(
    name='havarti',
    version='1.0',
    description='A quaint cheese shop that plays nicely in The Cloud.',
    author='Jake Basile',
    url='http://github.com/jakebasile/havarti',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask==0.9',
        'Jinja2==2.6',
        'SQLAlchemy==0.8.0b2',
        'Werkzeug==0.8.3',
        'amqp==1.0.6',
        'anyjson==0.3.3',
        'billiard==2.7.3.19',
        'boto==2.7.0',
        'celery==3.0.13',
        'distribute==0.6.31',
        'kombu==2.5.4',
        'python-cloudfiles==1.7.10',
        'python-dateutil==1.5',
        'redis==2.7.2',
        'requests==1.1.0',
        'wsgiref==0.1.2',
        'beautifulsoup4==4.1.3',
        'psycopg2==2.4.6',
        'gunicorn==0.17.2',
    ],
)
