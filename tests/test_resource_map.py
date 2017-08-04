#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_resource_map

:Synopsis:

:Author:
    servilla
  
:Created:
    3/21/17
"""

import logging

logger = logging.getLogger('test_resource_map')

import unittest
from datetime import datetime

from resource_map import ResourceMap
from package import Package


class TestResourceMap(unittest.TestCase):    
    package_str = 'knb-lter-nin.1.1'
    scope = 'knb-lter-nin'
    identifier = 1
    revision = 1
    datetime_str = '2017-02-23T13:09:29.166'
    datetime = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f')
    method_str = 'createDataPackage'
    owner_str = 'uid=LNO,o=LTER,dc=ecoinformatics,dc=org'
    
    def setUp(self):
        self.package = Package(event=Event())

    def tearDown(self):
        pass

    def test_build_resource_map(self):
        rm = ResourceMap(package=self.package)
        rm_xml = rm.get_resource_map()
        pass


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