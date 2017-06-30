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

import adapter_exceptions
import adapter_utilities
import properties

logger = logging.getLogger('resource')


class Resource(object):

    def __init__(self, resource=None):
        self.resource = resource
        self.type = self._get_resource_type()
        self.package_path = self._get_resource_package_path()
        self.data_name = self._get_data_name()
        self.d1_formats = adapter_utilities.get_d1_formats()

    def _build_system_metadata(self, principal_owner=None):
        sysmeta = {
            'identifier': self.resource,
            'formatId': self._get_format(),
            'size': self._get_size(),
            'checksum': {'value': self._get_checksum(),
                         'algorithm': properties.CHECKSUM_ALGORITHM},
            'rightsHolder': properties.DEFAULT_RIGHTS_HOLDER,
            'accessPolicy': self._get_acl_set(principal_owner=principal_owner),
            # e.g., [{'subject': 'public', 'permission': 'read'}]
            'replicationPolicy': {
                'replicationAllowed': None,
                'numberReplicas': None,
                'preferredMemberNode': [],  # e.g., 'urn:node:LTER'
                'blockedMemberNode': []  # e.g., 'urn:node:LTER'
            },
        }
        return sysmeta

    def _get_acl_set(self, principal_owner=None):
        """Return a list of EML access principals and permissions.

        :return: List of access principals and permissions
        """
        auth = (properties.GMN_USER, properties.GMN_PASSWD)
        eml_acl = None
        if self.type == properties.METADATA:
            url = self.resource.replace('/metadata/eml/', '/metadata/acl/eml/')
            r = adapter_utilities.requests_get_url_wrapper(url=url, auth=auth)
            if r is not None:
                eml_acl = r.text.strip()
        elif self.type == properties.REPORT:
            url = self.resource.replace('/report/eml/', '/report/acl/eml/')
            r = adapter_utilities.requests_get_url_wrapper(url=url, auth=auth)
            if r is not None:
                eml_acl = r.text.strip()
        elif self.type == properties.DATA:
            url = self.resource.replace('/data/eml/', '/data/acl/eml/')
            r = adapter_utilities.requests_get_url_wrapper(url=url, auth=auth)
            if r is not None:
                eml_acl = r.text.strip()

        acl = []
        if eml_acl is not None:
            tree = ET.ElementTree(ET.fromstring(eml_acl))
            for allow_rule in tree.iter('allow'):
                principal = allow_rule.find('./principal')
                permission = allow_rule.find('./permission')
                acl.append(
                    {'principal': principal.text,
                     'permission': permission.text})

        if principal_owner is not None:
            acl.append({'principal': principal_owner,
                        'permission': 'changePermission'})

        return acl

    def _get_base_url(self):
        base_url = None
        if properties.PRODUCTION in self.resource:
            base_url = 'https://' + properties.PRODUCTION + '/package/'
        elif properties.STAGING in self.resource:
            base_url = 'https://' + properties.STAGING + '/package/'
        elif properties.DEVELOPMENT in self.resource:
            base_url = 'https://' + properties.DEVELOPMENT + '/package/'
        return base_url

    def _get_checksum(self):
        checksum = None
        if self.type == properties.METADATA:
            url = self.resource.replace('/metadata/eml/',
                                        '/metadata/checksum/eml/')
            r = adapter_utilities.requests_get_url_wrapper(url=url)
            if r is not None:
                checksum = r.text.strip()
        elif self.type == properties.REPORT:
            url = self.resource.replace('/report/eml/', '/report/checksum/eml/')
            r = adapter_utilities.requests_get_url_wrapper(url=url)
            if r is not None:
                checksum = r.text.strip()
        elif self.type == properties.DATA:
            url = self.resource.replace('/data/eml/', '/data/checksum/eml/')
            r = adapter_utilities.requests_get_url_wrapper(url=url)
            if r is not None:
                checksum = r.text.strip()
        return checksum

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

    def _get_data_name(self):
        data_name = None
        if self.type == properties.DATA:
            data_name = self.resource.split('/')[-1]
        return data_name

    def _get_format(self):
        format_type = None
        if self.type == properties.METADATA:
            url = self.resource.replace('/metadata/eml/',
                                        '/metadata/format/eml/')
            r = adapter_utilities.requests_get_url_wrapper(url=url)
            if r is not None:
                eml_version = r.text.strip()
                if eml_version in self.d1_formats:
                    format_type = self.d1_formats[eml_version].formatId
        elif self.type == properties.REPORT:
            format_type = 'text/xml'
        elif self.type == properties.DATA:
            try:
                r = requests.head(self.resource, allow_redirects=True)
                if r.status_code == requests.codes.ok:
                    content_type = r.headers['Content-Type']
                    if content_type in self.d1_formats:
                        format_type = self.d1_formats[content_type].formatId
                    else:
                        format_type = 'application/octet-stream'
            except (requests.exceptions.RequestException,
                    requests.exceptions.BaseHTTPError,
                    requests.exceptions.HTTPError,
                    requests.exceptions.ConnectionError) as e:
                logger.error(e)
        return format_type

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

    def _get_size(self):
        size = None
        if self.type in [properties.METADATA, properties.REPORT]:
            url = self.resource
            r = adapter_utilities.requests_get_url_wrapper(url=url)
            if r is not None:
                size = r.headers['Content-Length']
        elif self.type == properties.DATA:
            url = self.resource.replace('/data/eml/', '/data/size/eml/')
            r = adapter_utilities.requests_get_url_wrapper(url=url)
            if r is not None:
                size = r.text.strip()
        if size is not None:
            size = int(size)
        return size

    def _make_metadata_url(self):
        return properties.PASTA_BASE_URL + 'metadata/eml/' + self.package_path

    def _requests_get_wrapped(self, url=None, auth=None):
        r = None
        try:
            r = requests.get(url=url, auth=auth)
            if r.status_code != requests.codes.ok:
                logger.error('Bad status code ({code}) for {url}'.format(
                    code=r.status_code, url=url))
                r = None
        except (requests.exceptions.RequestException,
                requests.exceptions.BaseHTTPError,
                requests.exceptions.HTTPError,
                requests.exceptions.ConnectionError) as e:
            logger.error(e)
        return r

    @property
    def public(self):
        """Determines if the resource is publicly accessible

        :return: boolean
        """
        public = False
        url = properties.PASTA_BASE_URL + 'authz?resourceId=' + self.resource
        r = adapter_utilities.requests_get_url_wrapper(url=url)
        status = None
        if r is not None:
            public = True
        return public

    def get_d1_sysmeta(self, principal_owner=None):
        """
        Build the DataONE system metadata pyxb object from the local system
        data structure. The 'principal owner' is passed in from the package
        object and applies to all resources in the package. The principal
        owner is the user who originally uploaded the data package into PASTA.

        :param principal_owner: Resource principal owner as string
        :return: DataONE system metadata as pyxb object
        """
        local_sys_meta = self._build_system_metadata(
            principal_owner=principal_owner)
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

    def get_science_metadata(self):
        scimeta = None
        r = adapter_utilities.requests_get_url_wrapper(url=self._make_metadata_url())
        if r is not None:
            scimeta = r.text.strip()
        return scimeta

    def get_type(self):
        return self.type

    def get_vendorSpecific_header(self):
        return {'VENDOR-GMN-REMOTE-URL': self.resource}