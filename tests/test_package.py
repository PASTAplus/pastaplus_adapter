#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_package

:Synopsis:

:Author:
    servilla
  
:Created:
    3/2/17
"""

import logging

logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.INFO)

import unittest
from datetime import datetime

import properties
from package import Package

logger = logging.getLogger('test_package')


class TestPackage(unittest.TestCase):
    package_str = 'knb-lter-nin.1.1'
    scope = 'knb-lter-nin'
    identifier = 1
    revision = 1
    datetime_str = '2017-02-23T13:09:29.166'
    datetime = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f')
    method_str = 'createDataPackage'
    owner_str = 'uid=LNO,o=LTER,dc=ecoinformatics,dc=org'
    doi_str = 'doi:10.6073/pasta/3bcc89b2d1a410b7a2c678e3c55055e1'
    number_of_resources = 3

    doi = 'doi:10.6073/pasta/3bcc89b2d1a410b7a2c678e3c55055e1'
    url = properties.PASTA_BASE_URL

    def setUp(self):
        self.package = Package(event=Event())

    def tearDown(self):
        pass

    def test_package(self):
        package = self.package.package
        self.assertEqual(TestPackage.package_str, package)

    def test_scope(self):
        scope = self.package.scope
        self.assertEqual(TestPackage.scope, scope)

    def test_identifier(self):
        identifier = self.package.identifier
        self.assertEqual(TestPackage.identifier, identifier)

    def test_revision(self):
        revision = self.package.revision
        self.assertEqual(TestPackage.revision, revision)

    def test_datetime(self):
        datetime = self.package.datetime
        self.assertEqual(TestPackage.datetime, datetime)
        datetime_str = datetime.strftime('%Y-%m-%dT%H:%M:%S.%f').rstrip('0')
        self.assertEqual(TestPackage.datetime_str, datetime_str)

    def test_method(self):
        method_str = self.package.method
        self.assertEqual(TestPackage.method_str, method_str)

    def test_resources(self):
        cnt = 2 # Begin with 2 metadata and report resources
        resources = self.package.resources
        cnt += len(resources[properties.DATA])
        self.assertEqual(TestPackage.number_of_resources, cnt)

    def test_public(self):
        self.assertTrue(self.package.public)

    def test_get_doi(self):
        self.assertEqual(TestPackage.doi, self.package.doi)


class Event(object):
    """
    Mock class to simulate a database recorded PASTA event from the
    adapter_queue.sqlite database.
    """
    def __init__(self):
        self.package = 'knb-lter-nin.1.1'
        self.datetime = datetime.strptime('2017-02-23T13:09:29.166',
                                          '%Y-%m-%dT%H:%M:%S.%f')
        self.method = 'createDataPackage'
        self.owner = 'uid=LNO,o=LTER,dc=ecoinformatics,dc=org'
        self.doi = 'doi:10.6073/pasta/3bcc89b2d1a410b7a2c678e3c55055e1'


if __name__ == '__main__':
    unittest.main()
