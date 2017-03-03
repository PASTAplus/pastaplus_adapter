#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_adapter_db

:Synopsis:

:Author:
    servilla
  
:Created:
    3/3/17
"""

import unittest
import logging

from adapter_db import QueueManager
from package import Package

logger = logging.getLogger('test_adapter_db')


class TestAdapterQueue(unittest.TestCase):

    def setUp(self):

        self.qm = QueueManager(queue='test_adapter_queue.sqlite')

        package_str = 'knb-lter-nin.12.14'
        datetime_str = '2017-02-23T13:09:29.166'
        event_str = 'createDataPackage'
        self.package = Package(package_str=package_str,
                               datetime_str=datetime_str,
                               event_str=event_str)

    def tearDown(self):
        self.qm.delete_queue()

    def test_add_event(self):
        self.qm.add_event(event_package=self.package)


if __name__ == '__main__':
    unittest.main()