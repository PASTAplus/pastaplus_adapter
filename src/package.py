#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: package

:Synopsis:
 
:Author:
    servilla

:Created:
    3/2/17
"""

import logging
from datetime import datetime

import requests

import properties
from resource import Resource


logger = logging.getLogger('package')


class Package(object):
    def __init__(self, package_str=None, datetime_str=None, method_str=None,
                 owner_str=None, doi_str=None):
        self._package_str = package_str.strip()
        self.package = self.package_str.split(".")
        self._scope = self.package[0]
        self._identifier = int(self.package[1])
        self._revision = int(self.package[2])
        self.package_path = self.package_str.replace('.', '/')
        self._resources = self._get_resources()

        if 'T' in datetime_str:
            self._datetime = datetime.strptime(datetime_str,
                                              '%Y-%m-%dT%H:%M:%S.%f')
        else:
            self._datetime = datetime.strptime(datetime_str,
                                              '%Y-%m-%d %H:%M:%S.%f')

        self._method = method_str.strip()
        self._owner = owner_str.strip()

        if doi_str is None:
            self._doi = self.package_purl
        else:
            self._doi = doi_str.strip()

    @property
    def package_str(self):
        return self._package_str

    @property
    def package_purl(self):
        return properties.PASTA_BASE_URL + 'eml/' + self.package_path

    @property
    def scope(self):
        return self._scope

    @property
    def identifier(self):
        return self._identifier

    @property
    def revision(self):
        return self._revision

    @property
    def resources(self):
        return self._resources

    @property
    def datetime(self):
        return self._datetime

    @property
    def method(self):
        return self._method

    @property
    def owner(self):
        return self._owner

    @property
    def doi(self):
        return self._doi

    def _get_resources(self):
        """
        Return the list data package resources without the reflexive package
        resource.

        :return: Resources as list of strings
        """
        resources = []
        url = self.package_purl
        try:
            r = requests.get(url=url)
            if r.status_code == requests.codes.ok:
                resources = r.text.split()
                for resource in resources:
                    if 'package/eml' in resource:
                        resources.remove(resource)
        except (requests.exceptions.RequestException,
                requests.exceptions.BaseHTTPError,
                requests.exceptions.HTTPError,
                requests.exceptions.ConnectionError) as e:
            logger.error(e)
        return resources

    def is_public(self):
        for resource in self._resources:
            r = Resource(resource=resource)
            if not r.is_public():
                return False
        return True


def main():
    return 0


if __name__ == "__main__":
    main()
