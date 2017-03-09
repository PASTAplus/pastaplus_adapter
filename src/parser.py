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
from datetime import timedelta

from lxml import etree

from queue import QueueManager
from package import Package
import adapter_utilities
import properties

logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.INFO)

logger = logging.getLogger('parser')


def bootstrap():
    url = properties.BASE_URL + '/changes/eml?'
    now = datetime.now()
    fromDate = datetime.strptime('2013-01-01T00:00:00.00',
                                 '%Y-%m-%dT%H:%M:%S.%f')
    while fromDate < now:
        toDate = fromDate + timedelta(days=1)
        fromDate_str = fromDate.strftime('%Y-%m-%dT%H:%M:%S.%f')
        toDate_str = toDate.strftime('%Y-%m-%dT%H:%M:%S.%f')
        logger.info('from: {f} -- to: {t}'.format(f=fromDate_str, t=toDate_str))
        parse(url=url, fromDate=fromDate_str, toDate=toDate_str)
        fromDate = toDate


def parse(url=None, fromDate=None, toDate=None, scope=None):

    if fromDate:
        url = url + 'fromDate=' + fromDate + '&'
    if toDate:
        url = url + 'toDate=' + toDate + '&'
    if scope:
        url = url + 'scope=' + scope

    qm = QueueManager()
    tree = etree.parse(url)
    for dataPackage in tree.getiterator('dataPackage'):
        packageId = dataPackage.find('./packageId')
        datetime = dataPackage.find('./date')
        method = dataPackage.find('./serviceMethod')
        p = packageId.text
        d = datetime.text
        m = method.text

        # Skip fromDate record(s) that already exist in queue
        if fromDate == datetime.text:
            logger.info('Skipping: {p} - {d} - {m}'.format(p=p, d=d, m=m))
        else:
            logger.info('Enqueue: {p} - {d} - {m}'.format(p=p, d=d, m=m))
            package = Package(package_str=p, datetime_str=d,
                              method_str=m)
            qm.enqueue(event_package=package)


def main():

    url = properties.BASE_URL + '/changes/eml?'
    qm = QueueManager()

    fromDate = qm.get_last_datetime()
    if not fromDate:
        bootstrap()
    else:
        parse(url=url, fromDate=fromDate)

    return 0


if __name__ == "__main__":
    main()