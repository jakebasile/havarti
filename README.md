# Havarti

Havarti is a quaint cheese shop that plays nicely in **The Cloud**.

## Installation Examples

Havarti is a [Flask][] application with a [Celery][] downloader that talks to itself with [Redis][] and uses [SQLAlchemy][] as an ORM. Setting these up is done differently depending on your deployment platform.

### Heroku Example

To host on [Heroku][] using [openredis][] and [Heroku Postgres][pg] and [S3][]:

    $ git clone git@github.com:jakebasile/havarti.git && cd havarti
    $ heroku apps:create
    $ heroku addons:add heroku-postgresql:dev
    $ heroku addons:add openredis:micro
    $ heroku config:add \
        STORAGE=s3storage \
        S3_ACCESS_KEY=<Your AWS Access Key> \
        S3_SECRET_KEY=<Your AWS Secret Key> \
        S3_BUCKET=<Name for an S3 Bucket> \
        REDIS_URI=<Redis URI from OpenRedis> \
        DB_URI=<Postgres URI from Heroku> \
        PASSCODE=<Your Super Secret Passcode>
    $ git push heroku master
    $ heroku scale web=1 downloader=1

### Local Example

To run locally, make sure you have Postgres and Redis running, then:

    $ pip install git+https://github.com/jakebasile/havarti.git 
    $ export \
        STORAGE=localstorage \
        REDIS_URI=<Redis URI> \
        DB_URI=<Postgres URI> \
        PASSCODE=<Your Super Secret Passcode>
    $ gunicorn -w 3 --preload 0.0.0.0:80 havarti:app & celery --app=havarti worker -l info

## Configuration Variables

Havarti is controlled through configuration variables set from environment variables.

### General Configuration

You must set the following variables in all cases:

    PORT=<Valid Port>
    PASSCODE=<Secret Passcode To Block Uploads>
    STORAGE=s3storage|rackspacestorage|localstorage
    DB_URI=<Postgres URI>
    REDIS_URI=<Redis URI>

You may also set these:

    DEBUG=True|False
    FALLBACK=<Index URL to cache from>

### S3 Configuration

For `s3storage`, you must set the following:

    S3_SECRET_KEY=<S3 Secret Key>
    S3_ACCESS_KEY=<S3 Access Key>
    S3_BUCKET=<S3 Bucket Name>

### Rackspace Configuration

For `rackspacestorage`, you must set the following:

    RACKSPACE_USERNAME=<Rackspace Username>
    RACKSPACE_KEY=<Rackspace API Key>
    RACKSPACE_CONTAINER=<Rackspace Container Name>

### Local Storage Configuration

`localstorage` has the following optional config variable:

    PACKAGE_CACHE=<Rooted Path - Default ~/.havarti-packages>

## Usage

Havarti acts as a proxy for [PyPI][pypi], intercepting requests for packages. When it recieves a package request, it follows a simple decision tree:

- Is package/version cached?
    - Yes: serve cached package.
    - No: Mark package for caching, serve PyPI package.

Havarti checks for new versions with every request, so you are always able to get the very newest version of whatever package you require (and then the new version will be cached from then on).

### Downloading

Just substitute your Havarti URL when using Pip.

    $ pip install -i http://random-phrase-5000.herokuapp.com/ reap

You can add this to your [pip.conf][] to save some keystrokes. If you add the `-i <Havarti_URL>` command to the top of your `requirements.txt` file all packages will route through Havarti when you `pip install -r requirements.txt`.

### Uploading

You can also upload packages to Havarti directly. These will not be pushed to PyPI, but are available to anyone with the Havarti url. To upload, just set up your [.pypirc][pypirc] file with your Havarti URL and passcode.

    [distutils]
    index-servers=
        havarti

    [havarti]
    repository:http://random-phrase-5000.herokuapp.com/
    username:havarti
    password:<Your Secret Passcode>

Then, you can upload to Havarti like usual by specifying it on the command line:

    $ python setup.py sdist upload -r havarti

## Contributing

If you want to contribute to Havarti, just fork and submit a pull request!

[Flask]: http://flask.pocoo.org/
[Celery]: http://celeryproject.org/
[Redis]: http://redis.io/
[heroku]: http://www.heroku.com/
[sqlalchemy]: http://sqlalchemy.org/
[openredis]: https://addons.heroku.com/openredis
[pg]: http://postgres.heroku.com/
[s3]: http://aws.amazon.com/s3/
[pypi]: http://pypi.python.org/pypi
[pip.conf]: http://www.pip-installer.org/en/latest/configuration.html#config-files
[cloudfiles]: http://www.rackspace.com/cloud/cloud_hosting_products/files/
[pypirc]: http://docs.python.org/distutils/packageindex.html#the-pypirc-file

