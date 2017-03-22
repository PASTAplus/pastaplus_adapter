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
    def __init__(self, package_str=None, datetime_str=None, method_str=None, owner_str=None):
        self.package_str = package_str.strip()
        self.package = self.package_str.split(".")
        self.scope = self.package[0]
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

    def get_package_str(self):
        return self.package_str

    def get_package_purl(self):
        return properties.PASTA_BASE_URL + 'eml/' + self.package_path

    def get_scope(self):
        return self.scope

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

    def _get_resources(self):
        """
        Return the list data package resources without the reflexive package resource.

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
        except Exception as e:
            logger.error(e)
        return resources

    def is_public(self):
        for resource in self.resources:
            r = Resource(resource=resource)
            if not r.is_public():
                return False
        return True

    def get_doi(self):
        doi = None
        url = properties.PASTA_BASE_URL + '/doi/eml/' + self.package_path
        try:
            r = requests.get(url=url)
            if r.status_code == requests.codes.ok:
                doi = r.text.strip()
        except Exception as e:
            logger.error(e)
        return doi


def main():
    return 0


if __name__ == "__main__":
    main()
