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

logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.INFO)

logger = logging.getLogger('parser')


class ChangeListParser(object):

    def __init__(self, baseUrl='http://pasta.lternet.edu/package/changes/eml',
                 fromDate=datetime.now().strftime(
                     '%Y-%m-%dT%H:%M:%S.%f').rstrip('0')):
        self.url = baseUrl + '?fromDate=' + fromDate
        self.tree = etree.parse(self.url)

    def list_packages(self):
        for dataPackage in self.tree.getiterator('dataPackageUpload'):
            packageId = dataPackage.find('./packageId')
            print packageId.text
            method = dataPackage.find('./serviceMethod')
            print method.text
            datetime = dataPackage.find('./date')
            print datetime.text
        #    for element in dataPackage:
        #       if element.tag == 'packageId':
        #          print element.text


def main():

    clp = ChangeListParser(baseUrl='http://pasta-s.lternet.edu/package'
                                   '/changes/eml',
                           fromDate='2017-02-01T00:00:00')
    clp.list_packages()

    return 0


if __name__ == "__main__":
    main()