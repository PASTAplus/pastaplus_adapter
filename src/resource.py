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
from sys_meta import SysMeta

logger = logging.getLogger('resource')


class ResourceBase(object):

    def __init__(self, url=None, owner=None):
        self._acl = None
        self._checksum_value = None
        self._checksum_algorithm = None
        self._d1_sys_meta = None
        self._file_name = None
        self._format_identifier = None
        self._identifier = url
        self._owner = owner
        self._replication_policy = None
        self._rights_holder = owner
        self._size = None
        self._url = url
        self._vendor_specific_header = {'VENDOR-GMN-REMOTE-URL': url}

    def _get_checksum_value(self, path, replacement):
        """
        Set the checksum value and algorithm for the given resource

        :param path: PASTA resource path fragment
        :param replacement: Modified path fragment for checksum value
        :return: None
        """
        url = self._url.replace(path, replacement)
        r = adapter_utilities.requests_get_url_wrapper(url=url)
        if r is not None:
            return r.text.strip()

    def _get_acl(self, path, replacement):
        """
        Return the EML access control list of principals and permissions

        :param path: PASTA resource path fragment
        :param replacement: Modified path fragment for PASTA EML ACL
        :param owner: Data package principal owner
        :return: Access control list
        """
        auth = (properties.GMN_USER, properties.GMN_PASSWD)
        eml_acl = None
        url = self._url.replace(path, replacement)
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
        if self._owner is not None:
            acl.append({'principal': self._owner,
                        'permission': 'changePermission'})
        return acl

    def _get_d1_access_policy(self, acl):
        """
        Return a DataONE system metadata access policy object based on the
        generated access policy found for the resource.

        :param acl: EML access control list of principals and permissions
        :return: DataONE access policy as pyxb object
        """
        accessPolicy = dataoneTypes_v_1.accessPolicy()
        for set in acl:
            accessRule = dataoneTypes_v_1.AccessRule()
            accessRule.subject.append(set['principal'])
            accessRule.permission.append(set['permission'])
            accessPolicy.append(accessRule)
        return accessPolicy

    def get_d1_sys_meta(self):
        sm = SysMeta()
        sm.access_policy = self._acl
        sm.checksum_algorithm = self._checksum_algorithm
        sm.checksum_value = self._checksum_value
        sm.format_identifier = self._format_identifier
        sm.identifier = self._identifier
        sm.replication_policy = self._replication_policy
        sm.rights_holder = self._rights_holder
        sm.size = self._size

        return sm.d1_sys_meta()

    @property
    def owner(self):
        return self._owner

    @property
    def url(self):
        return self._url

    @property
    def vendor_specific_header(self):
        return self._vendor_specific_header


class ResourceMetadata(ResourceBase):

    def __init__(self, url=None, owner=None):
        super(ResourceMetadata,self).__init__(url, owner)
        self._checksum_value = \
            self._get_checksum_value('/metadata/eml/', '/metadata/checksum/eml/')
        self._checksum_algorithm = properties.CHECKSUM_ALGORITHM
        self._acl = self._get_acl('/metadata/eml/', '/metadata/acl/eml/')
        self._format_identifier = self._get_format_id()
        self._size = self._get_size()

    def _get_format_id(self):
        d1_formats = adapter_utilities.get_d1_formats()
        format_id = None
        url = self._url.replace('/metadata/eml/', '/metadata/format/eml/')
        r = adapter_utilities.requests_get_url_wrapper(url=url)
        if r is not None:
            eml_version = r.text.strip()
            if eml_version in d1_formats:
                format_id = d1_formats[eml_version].formatId
        return format_id

    def _get_size(self):
        size = None
        r = adapter_utilities.requests_get_url_wrapper(url=self._url)
        if r is not None:
            size = int(r.headers['Content-Length'])
        return size


class ResourceReport(ResourceBase):

    def __init__(self, url=None, owner=None):
        super(ResourceReport,self).__init__(url, owner)
        self._checksum_value = \
            self._get_checksum_value('/report/eml/', '/report/checksum/eml/')
        self._checksum_algorithm = properties.CHECKSUM_ALGORITHM
        self._acl = self._get_acl('/report/eml/', '/report/acl/eml/')
        self._format_identifier = self._get_format_id()
        self._size = self._get_size()

    def _get_format_id(self):
        return 'text/xml'

    def _get_size(self):
        size = None
        r = adapter_utilities.requests_get_url_wrapper(url=self._url)
        if r is not None:
            size = int(r.headers['Content-Length'])
        return size


class ResourceData(ResourceBase):

    def __init__(self, url=None, owner=None):
        super(ResourceData,self).__init__(url, owner)
        self._checksum_value = \
            self._get_checksum_value('/data/eml/', '/data/checksum/eml/')
        self._checksum_algorithm = properties.CHECKSUM_ALGORITHM
        self._acl = self._get_acl('/data/eml/', '/data/acl/eml/')
        self._format_identifier = self._get_format_id()
        self._size = self._get_size()

    def _get_format_id(self):
        d1_formats = adapter_utilities.get_d1_formats()
        format_id = None
        try:
            r = requests.head(self._url, allow_redirects=True)
            if r.status_code == requests.codes.ok:
                content_type = r.headers['Content-Type']
                if content_type in d1_formats:
                    format_id = d1_formats[content_type].formatId
                else:
                    format_id = 'application/octet-stream'
        except Exception as e:
            logger.error(e)
        return format_id

    def _get_size(self):
        size = None
        url = self._url.replace('/data/eml/', '/data/size/eml/')
        r = adapter_utilities.requests_get_url_wrapper(url=url)
        if r is not None:
            size = int(r.text.strip())
        return size


class ResourceOre(ResourceBase):

    def __init__(self, url=None, owner=None):
        super(ResourceOre,self).__init__(url, owner)
