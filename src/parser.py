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

from adapter_db import QueueManager
from package import Package

logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.INFO)

logger = logging.getLogger('parser')

BASE_URL = 'http://pasta-d.lternet.edu/package/changes/eml/?'


def bootstrap():
    now = datetime.now()
    fromDate = datetime.strptime('2013-01-01T00:00:00.00',
                                 '%Y-%m-%dT%H:%M:%S.%f')
    while fromDate < now:
        toDate = fromDate + timedelta(days=1)
        fromDate_str = fromDate.strftime('%Y-%m-%dT%H:%M:%S.%f')
        toDate_str = toDate.strftime('%Y-%m-%dT%H:%M:%S.%f')
        logger.info('from: {f} -- to: {t}'.format(f=fromDate_str, t=toDate_str))
        parse(baseUrl=BASE_URL, fromDate=fromDate_str, toDate=toDate_str)
        fromDate = toDate


def parse(baseUrl=None, fromDate=None, toDate=None, scope=None):

    url = baseUrl
    if fromDate:
        url = url + 'fromDate=' + fromDate + '&'
    if toDate:
        url = url + 'toDate=' + toDate + '&'
    if scope:
        url = url + 'scope=' + scope

    qm = QueueManager()
    tree = etree.parse(url)
    for dataPackage in tree.getiterator('dataPackageUpload'):
        packageId = dataPackage.find('./packageId')
        datetime = dataPackage.find('./date')
        method = dataPackage.find('./serviceMethod')
        logger.info('Enqueue: {p} - {d} - {m}'.format(p=packageId.text,
                                                      d=datetime.text,
                                                      m=method.text))
        package = Package(package_str=packageId.text,
                          datetime_str=datetime.text, method_str=method.text)
        qm.enqueue(event_package=package)


def main():

    qm = QueueManager()

    fromDate = qm.get_last_datetime()
    if not fromDate:
        bootstrap()
    else:
        parse(baseUrl=BASE_URL, fromDate=fromDate)

    return 0


if __name__ == "__main__":
    main()