#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_package

:Synopsis:

:Author:
    servilla
  
:Created:
    3/2/17
"""

import unittest
import logging
from datetime import datetime

from package import Package


logger = logging.getLogger('test_package')


class TestPackage(unittest.TestCase):

    package_str = 'knb-lter-nin.1.1'
    scope = 'knb-lter-nin'
    identifier = 1
    revision = 11
    datetime_str = '2017-02-23T13:09:29.166'
    datetime = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f')
    method_str = 'createDataPackage'
    url = 'http://pasta-d.lternet.edu/package/'

    def setUp(self):
        self.package = Package(package_str=TestPackage.package_str,
                               datetime_str=TestPackage.datetime_str,
                               method_str=TestPackage.method_str)

    def tearDown(self):
        pass

    def test_get_package(self):
        package = self.package.get_package_str()
        self.assertEqual(TestPackage.package_str,package)

    def test_get_scope(self):
        scope = self.package.get_scope()
        self.assertEqual(TestPackage.scope,scope)

    def test_get_identifier(self):
        identifier = self.package.get_identifier()
        self.assertEqual(TestPackage.identifier,identifier)

    def test_get_revision(self):
        revision = self.package.get_revision()
        self.assertEqual(TestPackage.revision,revision)

    def test_get_datetime(self):
        datetime = self.package.get_datetime()
        self.assertEqual(TestPackage.datetime, datetime)
        datetime_str = datetime.strftime('%Y-%m-%dT%H:%M:%S.%f').rstrip('0')
        self.assertEqual(TestPackage.datetime_str, datetime_str)

    def test_get_method(self):
        method_str = self.package.get_method()
        self.assertEqual(TestPackage.method_str, method_str)

    def test_get_resource(self):
        resources = self.package.get_resources(url=TestPackage.url)
        print resources

if __name__ == '__main__':
    unittest.main()