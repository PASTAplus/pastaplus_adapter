#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

""":Mod: test_adapter_db

:Synopsis:

:Author:
    servilla
  
:Created:
    3/3/17
"""

import logging

logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.INFO)

import unittest

from queue import QueueManager
from package import Package

logger = logging.getLogger('test_queue')


class TestAdapterQueue(unittest.TestCase):
    def setUp(self):
        self.qm = QueueManager(queue='test_adapter_queue.sqlite')
        self.build_packages()

    def tearDown(self):
        self.qm.delete_queue()

    def test_enqueue(self):
        self.qm.enqueue(event_package=self.packages[0])
        self.assertFalse(self.qm.is_dequeued(event_package=self.packages[0]))

    def test_get_head(self):
        self.enqueue_all()
        package = self.qm.get_head()
        self.assertEqual(self.packages[0].get_package_str(),
                         package.get_package_str())

    def test_dequeue(self):
        self.enqueue_all()
        package_head = self.qm.get_head()
        self.qm.dequeue(event_package=package_head)
        self.assertTrue(self.qm.is_dequeued(event_package=package_head))

    def test_get_last_datetime(self):
        self.enqueue_all()
        datetime_str = self.qm.get_last_datetime()
        self.assertEqual(self.packages[5].get_datetime().strftime(
            '%Y-%m-%dT%H:%M:%S.%f').rstrip('0'), datetime_str)

    def test_get_predecessor(self):
        self.enqueue_all()
        package = self.packages[4]
        predecessor = self.qm.get_predecessor(package)
        print(predecessor.get_package_str())
        pass

    def build_packages(self):
        package_str1 = 'knb-lter-nin.12.14'
        datetime_str1 = '2016-12-12T03:09:29.166'
        method_str1 = 'createDataPackage'
        owner_str1 = 'uid=EDI,o=LTER,dc=ecoinformatics,dc=org'
        package1 = Package(package_str=package_str1,
                           datetime_str=datetime_str1,
                           method_str=method_str1,
                           owner_str=owner_str1)

        package_str2 = 'edi.1.1'
        datetime_str2 = '2017-01-03T18:23:29.3245'
        method_str2 = 'createDataPackage'
        owner_str2 = 'uid=EDI,o=LTER,dc=ecoinformatics,dc=org'
        package2 = Package(package_str=package_str2,
                           datetime_str=datetime_str2,
                           method_str=method_str2,
                           owner_str=owner_str2)

        package_str3 = 'edi.1.2'
        datetime_str3 = '2017-01-23T04:27:02.125'
        method_str3 = 'updateDataPackage'
        owner_str3 = 'uid=EDI,o=LTER,dc=ecoinformatics,dc=org'
        package3 = Package(package_str=package_str3,
                           datetime_str=datetime_str3,
                           method_str=method_str3,
                           owner_str=owner_str3)

        package_str4 = 'knb-lter-nin.12.18'
        datetime_str4 = '2017-02-23T13:09:29.166'
        method_str4 = 'updateDataPackage'
        owner_str4 = 'uid=EDI,o=LTER,dc=ecoinformatics,dc=org'
        package4 = Package(package_str=package_str4,
                           datetime_str=datetime_str4,
                           method_str=method_str4,
                           owner_str=owner_str4)

        package_str5 = 'edi.1.3'
        datetime_str5 = '2017-02-24T03:31:55.143'
        method_str5 = 'updateDataPackage'
        owner_str5 = 'uid=EDI,o=LTER,dc=ecoinformatics,dc=org'
        package5 = Package(package_str=package_str5,
                           datetime_str=datetime_str5,
                           method_str=method_str5,
                           owner_str=owner_str5)

        package_str6 = 'knb-lter-nin.12.18'
        datetime_str6 = '2017-03-01T02:01:45.66'
        method_str6 = 'deleteDataPackage'
        owner_str6 = 'uid=EDI,o=LTER,dc=ecoinformatics,dc=org'
        package6 = Package(package_str=package_str6,
                           datetime_str=datetime_str6,
                           method_str=method_str6,
                           owner_str=owner_str6)

        self.packages = (package1, package2, package3, package4, package5,
                         package6)

    def enqueue_all(self):
        for package in self.packages:
            self.qm.enqueue(event_package=package)


if __name__ == '__main__':
    unittest.main()
