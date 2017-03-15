#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: resource

:Synopsis:

:Author:
    servilla

:Created:
    3/10/17
"""

# Stdlib
import logging
import xml.etree.ElementTree as ET

# 3rd party
import requests

# Application
import properties
import adapter_utilities


logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.INFO)
logger = logging.getLogger('resource')


class Resource(object):
    def __init__(self, resource=None):
        self.resource = resource
        self.base_url = properties.PASTA_BASE_URL
        self.type = self._get_resource_type()
        self.package_path = self._get_resource_package_path()
        self.data_name = self._get_data_name()
        self.d1_formats = adapter_utilities.get_d1_formats()

    def get_type(self):
        return self.type

    def _get_base_url(self):
        base_url = None
        if properties.PRODUCTION in self.resource:
            base_url = 'https://' + properties.PRODUCTION + '/package/'
        elif properties.STAGING in self.resource:
            base_url = 'https://' + properties.STAGING + '/package/'
        elif properties.DEVELOPMENT in self.resource:
            base_url = 'https://' + properties.DEVELOPMENT + '/package/'
        return base_url

    def _get_resource_type(self):
        _type = None
        if 'package/eml' in self.resource:
            _type = 'package'
        elif 'package/metadata' in self.resource:
            _type = 'metadata'
        elif 'package/data' in self.resource:
            _type = 'data'
        elif 'package/report' in self.resource:
            _type = 'report'
        return _type

    def is_public(self):
        """Determines if the resource is publicly accessible

        :return: boolean
        """
        url = adapter_utilities.make_https(url=self.base_url) + \
              'authz?resourceId=' + self.resource
        r = requests.get(url)
        logger.info('Authz: {url} - {status}'.format(url=url, status=r.status_code))
        return r.status_code == requests.codes.ok

    def _get_resource_package_path(self):
        package_path = None
        if self.type in ['metadata', 'report']:
            scope = self.resource.split('/')[-3]
            identifier = self.resource.split('/')[-2]
            revision = self.resource.split('/')[-1]
            package_path = scope + '/' + identifier + '/' + revision
        elif self.type == 'data':
            scope = self.resource.split('/')[-4]
            identifier = self.resource.split('/')[-3]
            revision = self.resource.split('/')[-2]
            package_path = scope + '/' + identifier + '/' + revision
        return package_path

    def _get_data_name(self):
        data_name = None
        if self.type == 'data':
            data_name = self.resource.split('/')[-1]
        return data_name

    def _build_system_metadata(self):
        sysmeta = {
            'identifier': self.resource,
            'formatId': self._get_format(),
            'size': self._get_size(),
            'checksum': {'value': self._get_checksum(), 'algorithm': properties.CHECKSUM_ALGORITHM},
            'rightsHolder': None,
            'accessPolicy': self._get_acl(),  # e.g., {'subject': 'public', 'permission': 'read'}
            'replicationPolicy': {
                'replicationAllowed': None,
                'numberReplicas': None,
                'preferredMemberNode': [],  # e.g., 'urn:node:LTER'
                'blockedMemberNode': []  # e.g., 'urn:node:LTER'
            },

        }
        return sysmeta

    def _get_size(self):
        size = None
        if self.type in ['metadata', 'report']:
            r = requests.get(self.resource)
            size = r.headers['Content-Length']
        elif self.type == 'data':
            r = requests.get(self.resource.replace('/data/eml/', '/data/size/eml/'))
            size = r.text.strip()
        return int(size)

    def _get_format(self):
        _format = None
        if self.type == 'metadata':
            r = requests.get(self.resource.replace('/metadata/eml/', '/metadata/format/eml/'))
            eml_version = r.text.strip()
            if eml_version in self.d1_formats:
                _format = self.d1_formats[eml_version].formatId
        elif self.type == 'report':
            _format = 'text/xml'
        elif self.type == 'data':
            r = requests.head(self.resource)
            content_type = r.headers['Content-Type']
            if content_type in self.d1_formats:
                _format = self.d1_formats[content_type].formatId
            else:
                _format = 'application/octet-stream'
        return _format

    def _get_checksum(self):
        checksum = None
        if self.type == 'metadata':
            r = requests.get(self.resource.replace('/metadata/eml/', '/metadata/checksum/eml/'))
            checksum = r.text.strip()
        elif self.type == 'report':
            r = requests.get(self.resource.replace('/report/eml/', '/report/checksum/eml/'))
            checksum = r.text.strip()
        elif self.type == 'data':
            r = requests.get(self.resource.replace('/data/eml/', '/data/checksum/eml/'))
            checksum = r.text.strip()
        return checksum

    def _get_acl(self):
        """Return a list of EML access principals and permissions.

        :return: List of access principals and permissions
        """
        auth = (properties.GMN_USER, properties.GMN_PASSWD)
        eml_acl = None
        if self.type == 'metadata':
            r = requests.get(self.resource.replace('/metadata/eml/', '/metadata/acl/eml/'), auth=auth)
            eml_acl = r.text.strip()
        elif self.type == 'report':
            r = requests.get(self.resource.replace('/report/eml/', '/report/acl/eml/'), auth=auth)
            eml_acl = r.text.strip()
        elif self.type == 'data':
            r = requests.get(self.resource.replace('/data/eml/', '/data/acl/eml/'), auth=auth)
            eml_acl = r.text.strip()

        tree = ET.ElementTree(ET.fromstring(eml_acl))
        acl = []
        for allow_rule in tree.iter('allow'):
            principal = allow_rule.find('./principal')
            permission = allow_rule.find('./permission')
            acl.append({'principal': principal.text, 'permission': permission.text})
        return acl


def main():
    return 0


if __name__ == "__main__":
    main()
