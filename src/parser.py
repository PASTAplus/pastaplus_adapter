#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: parser

:Synopsis:
 
:Author:
    servilla

:Created:
    3/5/17
"""

import logging
from datetime import datetime

from lxml import etree

from adapter_db import QueueManager
from package import Package

logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.INFO)

logger = logging.getLogger('parser')


def main():

    qm = QueueManager()

    baseUrl='http://pasta-s.lternet.edu/package/changes/eml'
    fromDate = qm.get_last_datetime()
    #if not fromDate:
    fromDate='?fromDate=2017-02-01T00:00:00'

    tree = etree.parse(baseUrl + fromDate)
    for dataPackage in tree.getiterator('dataPackage'):
        packageId = dataPackage.find('./packageId')
        datetime = dataPackage.find('./date')
        method = dataPackage.find('./serviceMethod')
        logger.info('Enqueue: {p} - {d} - {m}'.format(p=packageId.text,
                                                      d=datetime.text,
                                                      m=method.text))
        package = Package(package_str=packageId.text,
                          datetime_str=datetime.text, method_str=method.text)
        qm.enqueue(event_package=package)

    return 0


if __name__ == "__main__":
    main()