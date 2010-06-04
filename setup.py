#!/usr/bin/env python

"""
@file setup.py
@author Skylar Saveland
@date 5/21/2010
@brief Setuptools configuration for djongobj
"""

version = '1.36'

sdict = {
    'name' : 'djongobj',
    'version' : version,
    'description' : 'add Mongo Document attr to model instances, and Collection attrs to model classes',
    'long_description' : 'classes to add to regular django model classes that allow you to interact with mongodb',
    'url': 'http://github.com/skyl/djongobj',
    'author' : 'Skylar Saveland',
    'author_email' : 'skylar.saveland@gmail.com',
    'maintainer' : 'Skylar Saveland',
    'maintainer_email' : 'skylar.saveland@gmail.com',
    'keywords' : ['MongoDB', 'PyMongo', 'key-value store', 'Django', 'Python', 'ORM', 'models'],
    'license' : 'MIT',
    'packages' : ['djongobj'],
    'test_suite' : 'tests',
    'classifiers' : [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'],
}

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(**sdict)
