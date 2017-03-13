#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_resource

:Synopsis:

:Author:
    servilla
  
:Created:
    3/10/17
"""

import unittest
import logging

import properties
from resource import Resource


logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.WARN)

logger = logging.getLogger('test_resource')


class TestResource(unittest.TestCase):

    metadata_resource = properties.PASTA_BASE_URL + 'metadata/eml/knb-lter-nin/1/1'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_build_system_metadata(self):
        resource = Resource(resource=TestResource.metadata_resource)
        sm = resource._build_system_metadata()
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()