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

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative
import os

Base = sqlalchemy.ext.declarative.declarative_base()

db_uri = os.environ['DB_URI']

db = sqlalchemy.create_engine(db_uri, convert_unicode=True)
db_session = sqlalchemy.orm.scoped_session(
    sqlalchemy.orm.sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db,
    )
)

Base.query = db_session.query_property()

def init_db():
    Base.metadata.create_all(bind=db)

class Package(Base):
    __tablename__ = 'packages'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(100), unique=True)

class Version(Base):
    __tablename__ = 'versions'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    version_code = sqlalchemy.Column(sqlalchemy.String(100))
    filename = sqlalchemy.Column(sqlalchemy.String(150), unique=True)
    date_cached = sqlalchemy.Column(sqlalchemy.DateTime())
    package_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('packages.id'))
    package = sqlalchemy.orm.relationship(
        'Package',
        backref=sqlalchemy.orm.backref(
            'versions',
            lazy='dynamic'
        ),
    )


