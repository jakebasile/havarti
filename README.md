# Havarti

Havarti is a quaint cheese shop that plays nicely in **The Cloud**.

## Installation

Havarti is a Flask app with a Celery downloader. Anything that can handle that can run it, but here are some suggestions on how to run it.

### Heroku

The default way of hosting Havarti is with [Heroku][heroku], [MongoHQ][mongohq], and [S3][s3].

    $ git clone git@github.com:jakebasile/havarti.git && cd havarti
    $ heroku apps:create --stack cedar
    $ heroku addons:add mongohq:free
    $ heroku config:add STORAGE=s3storage \
        AWS_ACCESS_KEY_ID=<Your AWS Access Key> \
        AWS_SECRET_KEY_ID=<Your AWS Secret Key> \
        MONGO_KEY=MONGOHQ_URL \
        PASSCODE=<Your Super Secret Passcode>
    $ git push heroku master
    $ heroku scale web=1 downloader=1

### Local

Maybe you don't want to be a cool cat and run Havarti on Heroku. You want to run it locally. Here's one way to do it. First, install Havarti somewhere:

    $ virtualenv havarti-install 
    $ cd havarti-install
    $ source bin/activate
    $ pip install havarti gunicorn supervisor

This will install Havarti, Gunicorn, and Supervisor to run it all. Now, make a `supervisord.conf` file in this directory:

    [unix_http_server]
    file=supervisord.sock
    chmod=0777

    [rpcinterface:supervisor]
    supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

    [supervisord]
    logfile=logs/supervisor.txt
    loglevel=info
    pidfile=supervisord.pid

    [supervisorctl]
    serverurl=unix://supervisord.sock

    [program:mongodb]
    command=mongod
    stdout_logfile=logs/mongodb.txt
    stderr_logfile=logs/mongodb-err.txt
    priority=1

    [program:havarti]
    command=bin/gunicorn -w 3 --preload -b 0.0.0.0:80 havarti:app
    stdout_logfile=logs/havarti.txt
    stderr_logfile=logs/havarti-err.txt
    environment=STORAGE=localstorage,PACKAGE_CACHE=/var/havarti,PASSCODE=<Secret Passcode>
    priority=2

    [program:celery]
    command=bin/celery --app=havarti worker -l info
    stdout_logfile=logs/celery.txt
    stderr_logfile=logs/celery-err.txt
    environment=STORAGE=localstorage,PACKAGE_CACHE=/var/havarti,PASSCODE=<Secret Passcode>
    priority=3

This assumes that you have MongoDB installed previously. Then, again from this directory, just create the directories needed and start Supervisor!

    $ mkdir logs 
    $ sudo mkdir -p /data/db
    $ sudo bin/supervisord

You can now control the processes through `supervisorctl`. Check out [Supervisor's documentation][superdoc] for more info on it.

### Package Cache Options

You can use [Rackspace Cloud Files][cloudfiles] to store the cache by changing the config line to:

    $ heroku config:add STORAGE=rackspacestorage \
        RACKSPACE_USERNAME=<Your Rackspace Username> \
        RACKSPACE_KEY=<Your Rackspace API Key> \
        MONGO_KEY=MONGOHQ_URL \
        PASSCODE=<Your Super Secret Passcode>
        
Alternatively a [GridFS][gridfs] option is available by changing the config line to:

    $ heroku config:add STORAGE=mongostorage \
        MONGO_KEY=MONGOHQ_URL \
        PASSCODE=<Your Super Secret Passcode>
        
For **local use only** a file system based cache is avaliable. It can be used by specifying it in the `supervisord.conf`. Packages will be cached in `~/.havarti-packages/` by default. 

    [program:havarti]
    command=bin/gunicorn -w 3 --preload -b 0.0.0.0:80 havarti:app
    stdout_logfile=logs/havarti.txt
    stderr_logfile=logs/havarti-err.txt
    environment=STORAGE=localstorage,PASSCODE=<Secret Passcode>
    priority=2

    [program:celery]
    command=bin/celery --app=havarti worker -l info
    stdout_logfile=logs/celery.txt
    stderr_logfile=logs/celery-err.txt
    environment=STORAGE=localstorage,PASSCODE=<Secret Passcode>
    priority=3
	
The cache directory can also be specified by adding `PACKAGE_CACHE` to the above example.

	[program:havarti]
	command=bin/gunicorn -w 3 --preload -b 0.0.0.0:80 havarti:app
	stdout_logfile=logs/havarti.txt
	stderr_logfile=logs/havarti-err.txt
	environment=STORAGE=localstorage,PACKAGE_CACHE=/var/havarti,PASSCODE=<Secret Passcode>
	priority=2

	[program:celery]
	command=bin/celery --app=havarti worker -l info
	stdout_logfile=logs/celery.txt
	stderr_logfile=logs/celery-err.txt
	environment=STORAGE=localstorage,PACKAGE_CACHE=/var/havarti,PASSCODE=<Secret Passcode>
	priority=3

## Usage

Havarti acts as a proxy for [PyPI][pypi], intercepting requests for packages. When it recieves a package request, it follows a simple decision tree:

- Is package/version cached?
    - Yes: serve cached package.
    - No: Mark package for caching, serve PyPI package.

Havarti checks for new versions with every request, so you are always able to get the very newest version of whatever package you require (and then the new version will be cached from then on).

### Downloading

Just substitute your Havarti Index URL when using Pip. Your Havarti Index URL is wherever you hosted Havarti + '/i/', e.g. 'http://random-phrase-5000.herokuapp.com/i/'.

    $ pip install -i http://random-phrase-5000.herokuapp.com/i/ reap

You can add this to your [pip.conf][] to save some keystrokes.

### Uploading

You can also upload packages to Havarti directly. These will not be pushed to PyPI, but are available to anyone with the Havarti url. To upload, just set up your [.pypirc][pypirc] file with your Havarti upload URL and passcode. Your Havarti Upload URL is wherever you hosted Havarti + '/u/', e.g. 'http://random-phrase-5000.herokuapp.com/u/':

    [distutils]
    index-servers=
        havarti

    [havarti]
    repository:http://random-phrase-5000.herokuapp.com/u/
    username:havarti
    password:<Your Secret Passcode>

Then, you can upload to Havarti like usual by specifying it on the command line:

    $ python setup.py sdist upload -r havarti

## Contributing

If you want to contribute to Havarti, just fork and submit a pull request!

## Changelog

- v0.4
    - Fixed logging into MongoDB with upstream upgrade.
    - Removed uneeded and updated requirements.
- v0.3
	- Added Mongo GridFS storage option.
    - Properly handled unfound packages.
    - Added a timeout to main index requests.
- v0.2
    - Passcode protected uploads.
    - Now finds more types of source distributions.
    - Added ability to specify local storage location.
- v0.1 
    - Initial Release.

[heroku]: http://www.heroku.com/
[mongohq]: http://mongohq.com/
[s3]: http://aws.amazon.com/s3/
[pypi]: http://pypi.python.org/pypi
[pip.conf]: http://www.pip-installer.org/en/latest/configuration.html#config-files
[cloudfiles]: http://www.rackspace.com/cloud/cloud_hosting_products/files/
[superdoc]: http://supervisord.org/
[pypirc]: http://docs.python.org/distutils/packageindex.html#the-pypirc-file
[gridfs]: http://www.mongodb.org/display/DOCS/GridFS

