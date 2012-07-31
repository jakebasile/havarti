from setuptools import setup, find_packages

setup(
    name='havarti',
    version='0.2',
    description='A quaint cheese shop that plays nicely in The Cloud.',
    author='Jake Basile',
    author_email='jakebasile@me.com',
    url='https://github.com/jakebasile/havarti',
    download_url='https://github.com/downloads/jakebasile/havarti/havarti-0.2.tar.gz',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        ['Flask==0.9'],
        ['Flask-PyMongo==0.1.2'],
        ['Jinja2==2.6'],
        ['Werkzeug==0.8.3'],
        ['amqplib==1.0.2'],
        ['anyjson==0.3.3'],
        ['beautifulsoup4==4.1.1'],
        ['billiard==2.7.3.10'],
        ['boto==2.5.2'],
        ['celery==3.0.3'],
        ['celery-with-mongodb==3.0'],
        ['distribute==0.6.24'],
        ['kombu==2.2.6'],
        ['pymongo==2.2.1'],
        ['python-cloudfiles==1.7.10'],
        ['python-dateutil==1.5'],
        ['requests==0.13.3'],
    ],
)
