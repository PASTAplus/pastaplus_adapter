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
        self.identifier = int(self.package[1])
        self.revision = int(self.package[2])
        self.package_path = self.package_str.replace('.', '/')
        self.resources = self._get_resources()

        if 'T' in datetime_str:
            self.datetime = datetime.strptime(datetime_str,
                                              '%Y-%m-%dT%H:%M:%S.%f')
        else:
            self.datetime = datetime.strptime(datetime_str,
                                              '%Y-%m-%d %H:%M:%S.%f')

        self.method = method_str.strip()
        self.owner = owner_str.strip()

        if doi_str is None:
            self.doi = self.package_purl
        else:
            self.doi = doi_str.strip()

    @property
    def package_str(self):
        return self._package_str

    @property
    def package_purl(self):
        return properties.PASTA_BASE_URL + 'eml/' + self.package_path

    @property
    def scope(self):
        return self._scope

    def get_identifier(self):
        return self.identifier

    def get_revision(self):
        return self.revision

    def get_resources(self):
        return self.resources

    def get_datetime(self):
        return self.datetime

    def get_method(self):
        return self.method

    def get_owner(self):
        return self.owner

    def get_doi(self):
        return self.doi

    def _get_resources(self):
        """
        Return the list data package resources without the reflexive package
        resource.

        :return: Resources as list of strings
        """
        resources = []
        url = properties.PASTA_BASE_URL + 'eml/' + self.package_path
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
        for resource in self.resources:
            r = Resource(resource=resource)
            if not r.is_public():
                return False
        return True


def main():
    return 0


if __name__ == "__main__":
    main()
