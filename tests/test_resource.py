#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_resource

:Synopsis:

:Author:
    servilla
  
:Created:
    3/10/17
"""

import logging
import unittest

from datetime import datetime

import properties
from resource import Resource
from package import Package


logger = logging.getLogger('test_resource')


class TestResource(unittest.TestCase):

    metadata_resource = properties.PASTA_BASE_URL + 'metadata/eml/knb-lter-nin/1/1'
    package_str = 'knb-lter-nin.1.1'
    scope = 'knb-lter-nin'
    identifier = 1
    revision = 1
    datetime_str = '2017-02-23T13:09:29.166'
    datetime = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f')
    method_str = 'createDataPackage'
    doi = 'doi:10.6073/pasta/3bcc89b2d1a410b7a2c678e3c55055e1'
    url = properties.PASTA_BASE_URL


    def setUp(self):
        self.package = Package(package_str=TestResource.package_str,
                               datetime_str=TestResource.datetime_str,
                               method_str=TestResource.method_str)

    def tearDown(self):
        pass

    def test_build_system_metadata(self):
        resources = self.package.get_resources()
        for resource in resources:
            resource = Resource(resource=resource)
            sm = resource._build_system_metadata()
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()