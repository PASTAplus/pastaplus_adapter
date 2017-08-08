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
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.WARN)

from datetime import datetime
from datetime import timedelta
import xml.etree.ElementTree as ET

import requests

from event import Event
from lock import Lock
import properties
from queue_manager import QueueManager


logger = logging.getLogger('poll_manager')


def bootstrap():
    url = properties.PASTA_BASE_URL + '/changes/eml?'
    now = datetime.now()
    fromDate = datetime.strptime(properties.FROM_DATE,
                                 '%Y-%m-%dT%H:%M:%S.%f')
    while fromDate < now:
        toDate = fromDate + timedelta(days=1)
        fromDate_str = fromDate.strftime('%Y-%m-%dT%H:%M:%S.%f')
        toDate_str = toDate.strftime('%Y-%m-%dT%H:%M:%S.%f')
        logger.warn('from: {f} -- to: {t}'.format(f=fromDate_str, t=toDate_str))
        parse(url=url, fromDate=fromDate_str, toDate=toDate_str)
        fromDate = toDate


def parse(url=None, fromDate=None, toDate=None, scope=properties.SCOPE):
    """
    Parse the PASTA list of changes XML based on the query parameters provided
     
    :param url: changes URL as a String
    :param fromDate: fromDate as a date formatted String '%Y-%m-%dT%H:%M:%S.%f'
    :param toDate: toDate as a data formatted String '%Y-%m-%dT%H:%M:%S.%f'
    :param in_scope: in_scope filter value (only one) as a String for changes
                     query
    :return: 0 if successful, 1 otherwise
    """
    if fromDate:
        url = url + 'fromDate=' + fromDate + '&'
    if toDate:
        url = url + 'toDate=' + toDate + '&'
    if scope:
        url = url + 'scope=' + scope

    try:
        r = requests.get(url)
    except (requests.exceptions.RequestException,
            requests.exceptions.BaseHTTPError,
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError) as e:
        logger.error(e)
        return 1

    if r.status_code == requests.codes.ok:
        qm = QueueManager()
        tree = ET.ElementTree(ET.fromstring(r.text.strip()))
        for dataPackage in tree.iter('dataPackage'):
            package = dataPackage.find('./packageId')
            date = dataPackage.find('./date')
            method = dataPackage.find('./serviceMethod')
            owner = dataPackage.find('./principal')
            doi = dataPackage.find('./doi')

            event = Event()
            event.package = package.text
            event.datetime = date.text
            event.method = method.text
            event.owner = owner.text
            event.doi = doi.text

            # Skip fromDate record(s) that already exist in queue
            if fromDate.rstrip('0') == date.text:
                msg = 'Skipping: {} - {} - {}'.format(package.text, date.text,
                                                      method.text)
                logger.warn(msg)
            else:
                # Provide additional filter for multiple scope values
                package_scope = event.package.split('.')[0]
                if package_scope in properties.PASTA_WHITELIST:
                    msg = 'Enqueue: {} - {} - {}'.format(package.text,
                                                         date.text, method.text)
                    logger.warn(msg)
                    qm.enqueue(event=event)
                else:
                    logger.info('Package {} out of scope'.format(package.text))

        return 0
    else:
        logger.warn('Bad status code ({code}) for {url}'.format(
            code=r.status_code, url=url))
        return 1


def main():

    lock = Lock('/tmp/poll_manager.lock')
    if lock.locked:
        logger.error('Lock file {} exists, exiting...'.format(lock.lock_file))
        return 1
    else:
        lock.acquire()
        logger.warn('Lock file {} acquired'.format(lock.lock_file))

    url = properties.PASTA_BASE_URL + '/changes/eml?'
    qm = QueueManager()

    fromDate = datetime.strftime(qm.get_last_datetime(), '%Y-%m-%dT%H:%M:%S.%f')
    if not fromDate:
        bootstrap()
    else:
        parse(url=url, fromDate=fromDate)

    lock.release()
    logger.warn('Lock file {} released'.format(lock.lock_file))
    return 0


if __name__ == "__main__":
    main()
