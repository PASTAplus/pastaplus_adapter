#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: resource

:Synopsis:

:Author:
    servilla

:Created:
    3/10/17
"""

import logging

import requests

import properties
import adapter_utilities

logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.INFO)

logger = logging.getLogger('resource')


class Resource(object):

    def __init__(self, resource=None):
        self.resource = resource
        self.type = self._get_resource_type()

    def get_type(self):
        return self.type

    def _get_resource_type(self):
        type = None
        if 'package/eml' in self.resource:
            type = 'package'
        elif 'package/metadata' in self.resource:
            type = 'metadata'
        elif 'package/data' in self.resource:
            type = 'data'
        elif 'package/report' in self.resource:
            type = 'report'
        return type

    def is_public(self, url=None):
        """Determines if the resource is publicly accessible

        :param url: The PASTA base url
        :return: boolean
        """
        url = adapter_utilities.makeHttps(url=url) + \
              'authz?resourceId=' + self.resource
        r = requests.get(url)
        logger.info('Authz: {url} - {status}'.format(url=url, status= r.status_code))
        return (r.status_code == requests.codes.ok)

    def _build_system_metadata(self):
        sysmeta = {}
        identifier = self.resource
        formatId = None
        size = 0

    def _get_size(self):
        x=9


def main():
    return 0


if __name__ == "__main__":
    main()