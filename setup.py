import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='openimis-be-dhis2_etl',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    license='GNU AGPL v3',
    description='The openIMIS Backend to send data to DHIS2.',
    # long_description=README,
    url='https://openimis.org/',
    author='Patrick Delcroix',
    author_email='patrick.delcroix@swisstph.ch',
    install_requires=[
        'django',
        'django-db-signals',
        'dhis2.py',
        'email-validator',
        'pydantic',
        'dict2obj',
        'isodate==0.6.1',
        'python-dateutil==2.8.2'
    ],   
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
