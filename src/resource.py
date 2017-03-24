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
import xml.etree.ElementTree as ET

import requests
import d1_common.types.exceptions
import d1_common.types.generated.dataoneTypes_v1 as dataoneTypes_v_1
import d1_common.types.generated.dataoneTypes_v2_0 as dataoneTypes_v2_0

import properties
import adapter_utilities

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

    def is_public(self):
        """Determines if the resource is publicly accessible

        :return: boolean
        """
        url = adapter_utilities.make_https(url=self.base_url) + \
              'authz?resourceId=' + self.resource
        r = requests.get(url)
        logger.info(
            'Authz: {url} - {status}'.format(url=url, status=r.status_code))
        return r.status_code == requests.codes.ok

    def get_d1_sysmeta(self,
                       rights_holder=properties.DEFAULT_RIGHTS_HOLDER):
        """
        Build the DataONE system metadata pyxb object from the local system
        data structure. The 'rights holder' is passed in from the package
        object and applies to all resources in the package.

        :param rights_holder: Resource rights holder as string
        :return: DataONE system metadata as pyxb object
        """
        local_sys_meta = self._build_system_metadata(
            rights_holder=rights_holder)
        d1_sys_meta = dataoneTypes_v2_0.systemMetadata()
        d1_sys_meta.serialVersion = 1
        d1_sys_meta.identifier = local_sys_meta['identifier']
        d1_sys_meta.size = local_sys_meta['size']
        d1_sys_meta.formatId = local_sys_meta['formatId']
        d1_sys_meta.rightsHolder = local_sys_meta['rightsHolder']
        d1_sys_meta.checksum = dataoneTypes_v_1.Checksum(
            local_sys_meta['checksum']['value'])
        d1_sys_meta.checksum.algorithm = local_sys_meta['checksum']['algorithm']
        d1_sys_meta.accessPolicy = self._get_d1_access_policy(
            acl_set=local_sys_meta['accessPolicy'])
        return d1_sys_meta

    def get_vendorSpecific_header(self):
        return {'VENDOR-GMN-REMOTE-URL': self.resource}

    def _get_d1_access_policy(self, acl_set=None):
        """
        Return a DataONE system metadata access policy object based on the
        generated access policy found for the resource.

        :param acl_set: Local resource access policy as a list
        :return: DataONE access policy as pyxb object
        """
        accessPolicy = dataoneTypes_v_1.accessPolicy()
        for acl in acl_set:
            accessRule = dataoneTypes_v_1.AccessRule()
            accessRule.subject.append(acl['principal'])
            accessRule.permission.append(acl['permission'])
            accessPolicy.append(accessRule)
        return accessPolicy

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
        resource_type = None
        if 'package/eml' in self.resource:
            resource_type = properties.PACKAGE
        elif 'package/metadata' in self.resource:
            resource_type = properties.METADATA
        elif 'package/data' in self.resource:
            resource_type = properties.DATA
        elif 'package/report' in self.resource:
            resource_type = properties.REPORT
        return resource_type

    def _get_resource_package_path(self):
        package_path = None
        if self.type in [properties.METADATA, properties.REPORT]:
            scope = self.resource.split('/')[-3]
            identifier = self.resource.split('/')[-2]
            revision = self.resource.split('/')[-1]
            package_path = scope + '/' + identifier + '/' + revision
        elif self.type == properties.DATA:
            scope = self.resource.split('/')[-4]
            identifier = self.resource.split('/')[-3]
            revision = self.resource.split('/')[-2]
            package_path = scope + '/' + identifier + '/' + revision
        return package_path

    def _get_data_name(self):
        data_name = None
        if self.type == properties.DATA:
            data_name = self.resource.split('/')[-1]
        return data_name

    def _build_system_metadata(self, rights_holder=None):
        sysmeta = {
            'identifier': self.resource,
            'formatId': self._get_format(),
            'size': self._get_size(),
            'checksum': {'value': self._get_checksum(),
                         'algorithm': properties.CHECKSUM_ALGORITHM},
            'rightsHolder': rights_holder,
            'accessPolicy': self._get_acl_set(),
            # e.g., [{'subject': 'public', 'permission': 'read'}]
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
        if self.type in [properties.METADATA, properties.REPORT]:
            r = requests.get(self.resource)
            size = r.headers['Content-Length']
        elif self.type == properties.DATA:
            r = requests.get(
                self.resource.replace('/data/eml/', '/data/size/eml/'))
            size = r.text.strip()
        return int(size)

    def _get_format(self):
        format_type = None
        if self.type == properties.METADATA:
            r = requests.get(self.resource.replace('/metadata/eml/',
                                                   '/metadata/format/eml/'))
            eml_version = r.text.strip()
            if eml_version in self.d1_formats:
                format_type = self.d1_formats[eml_version].formatId
        elif self.type == properties.REPORT:
            format_type = 'text/xml'
        elif self.type == properties.DATA:
            r = requests.head(self.resource, allow_redirects=True)
            content_type = r.headers['Content-Type']
            if content_type in self.d1_formats:
                format_type = self.d1_formats[content_type].formatId
            else:
                format_type = 'application/octet-stream'
        return format_type

    def _get_checksum(self):
        checksum = None
        if self.type == properties.METADATA:
            r = requests.get(self.resource.replace('/metadata/eml/',
                                                   '/metadata/checksum/eml/'))
            checksum = r.text.strip()
        elif self.type == properties.REPORT:
            r = requests.get(
                self.resource.replace('/report/eml/', '/report/checksum/eml/'))
            checksum = r.text.strip()
        elif self.type == properties.DATA:
            r = requests.get(
                self.resource.replace('/data/eml/', '/data/checksum/eml/'))
            checksum = r.text.strip()
        return checksum

    def _get_acl_set(self):
        """Return a list of EML access principals and permissions.

        :return: List of access principals and permissions
        """
        auth = (properties.GMN_USER, properties.GMN_PASSWD)
        eml_acl = None
        if self.type == properties.METADATA:
            r = requests.get(
                self.resource.replace('/metadata/eml/', '/metadata/acl/eml/'),
                auth=auth)
            eml_acl = r.text.strip()
        elif self.type == properties.REPORT:
            r = requests.get(
                self.resource.replace('/report/eml/', '/report/acl/eml/'),
                auth=auth)
            eml_acl = r.text.strip()
        elif self.type == properties.DATA:
            r = requests.get(
                self.resource.replace('/data/eml/', '/data/acl/eml/'),
                auth=auth)
            eml_acl = r.text.strip()

        tree = ET.ElementTree(ET.fromstring(eml_acl))
        acl = []
        for allow_rule in tree.iter('allow'):
            principal = allow_rule.find('./principal')
            permission = allow_rule.find('./permission')
            acl.append(
                {'principal': principal.text, 'permission': permission.text})
        return acl


def main():
    return 0


if __name__ == "__main__":
    main()
