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

logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.INFO)

from datetime import datetime
from datetime import timedelta
import xml.etree.ElementTree as ET

import requests

from queue_manager import QueueManager
from package import Package
import adapter_utilities
import properties


logger = logging.getLogger('poll_manager')


def bootstrap():
    url = properties.PASTA_BASE_URL + '/changes/eml?'
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

    r = requests.get(url)

    qm = QueueManager()
    tree = ET.ElementTree(ET.fromstring(r.text.strip()))
    for dataPackage in tree.iter('dataPackage'):
        packageId = dataPackage.find('./packageId')
        datetime = dataPackage.find('./date')
        method = dataPackage.find('./serviceMethod')
        owner = dataPackage.find('./principal')
        p = packageId.text
        d = datetime.text
        m = method.text
        o = owner.text

        # Skip fromDate record(s) that already exist in queue
        if fromDate == datetime.text:
            logger.info('Skipping: {p} - {d} - {m}'.format(p=p, d=d, m=m))
        else:
            package = Package(package_str=p, datetime_str=d, method_str=m, owner_str=o)
            if package.get_scope() in properties.PASTA_WHITELIST:
                logger.info('Enqueue: {p} - {d} - {m}'.format(p=p, d=d, m=m))
                qm.enqueue(event_package=package)


def main():
    url = properties.PASTA_BASE_URL + '/changes/eml?'
    qm = QueueManager()

    fromDate = qm.get_last_datetime()
    if not fromDate:
        bootstrap()
    else:
        parse(url=url, fromDate=fromDate)

    return 0


if __name__ == "__main__":
    main()
