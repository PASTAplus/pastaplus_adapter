#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

""":Mod: test_resource

:Synopsis:

:Author:
    servilla
  
:Created:
    3/10/17
"""

import logging

logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.INFO)

import unittest
from datetime import datetime

import properties
from resource import Resource
from package import Package

logger = logging.getLogger('test_resource')


class TestResource(unittest.TestCase):
    metadata_resource = properties.PASTA_BASE_URL + \
                        'metadata/eml/knb-lter-nin/1/1'
    package_str = 'knb-lter-nin.1.1'
    scope = 'knb-lter-nin'
    identifier = 1
    revision = 1
    datetime_str = '2017-02-23T13:09:29.166'
    datetime = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f')
    method_str = 'createDataPackage'
    owner_str = 'uid=LNO,o=LTER,dc=ecoinformatics,dc=org'
    doi = 'doi:10.6073/pasta/3bcc89b2d1a410b7a2c678e3c55055e1'
    url = properties.PASTA_BASE_URL
    scimeta_size = 48856 # For https://pasta-d.lternet.edu/package/metadata/eml/knb-lter-nin/1/1

    def setUp(self):
        self.package = Package(package_str=TestResource.package_str,
                               datetime_str=TestResource.datetime_str,
                               method_str=TestResource.method_str,
                               owner_str=TestResource.owner_str)

    def tearDown(self):
        pass

    def test_build_system_metadata(self):
        resources = []
        resources.append(self.package.resources[properties.METADATA])
        for resource in self.package.resources[properties.DATA]:
            resources.append(resource)

        for resource in resources:
            r = Resource(resource=resource)
            sysmeta = r.get_d1_sysmeta(
                principal_owner=self.package.owner)
            self.assertEqual(resource, sysmeta.identifier.value())
            print(sysmeta.toxml())

    def test_get_science_metadata(self):
        resources = []
        resources.append(self.package.resources[properties.METADATA])
        for resource in self.package.resources[properties.DATA]:
            resources.append(resource)

        for resource in resources:
            r = Resource(resource=resource)
            scimeta = r.get_science_metadata()
            self.assertEqual(self.scimeta_size, len(scimeta))



if __name__ == '__main__':
    unittest.main()
