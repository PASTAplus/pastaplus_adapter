#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: resource_map

:Synopsis:
 
:Author:
    servilla

:Created:
    3/21/17
"""

import logging

logger = logging.getLogger('resource_map')

import xml.etree.ElementTree as ET

import requests
import d1_client.cnclient_2_0
import d1_client.mnclient_2_0
import d1_client.data_package
import d1_common.checksum
import d1_common.types.exceptions
import d1_common.types.generated.dataoneTypes_v1 as dataoneTypes_v_1
import d1_common.types.generated.dataoneTypes_v2_0 as dataoneTypes_v2_0

import properties
from resource import Resource


class ResourceMap(object):
    def __init__(self, package=None):
        self.package = package
        self.pid = self.package.get_doi()
        if self.pid is None:
            self.pid = self.package.package_purl
        self.metadata_pid, self.resource_pids = self._build_package_pids()
        self.resource_map = self._generate_resource_map()

    def get_resource_map(self):
        return self.resource_map

    def get_resource_map_system_metadata(self, principal_owner=None):
        system_metadata = self._build_system_metadata(
            principal_owner=principal_owner)
        return system_metadata

    def get_resource_map_pid(self):
        return self.pid

    def _build_package_pids(self):
        metadata_pid = None
        resource_pids = []
        resources = self.package.get_resources()
        for resource in resources:
            r = Resource(resource=resource)
            if r.get_type() == properties.METADATA:
                metadata_pid = r.resource
            else:
                resource_pids.append(resource)
        return metadata_pid, resource_pids

    def _generate_resource_map(self):
        resource_map_generator = d1_client.data_package.ResourceMapGenerator(
            properties.D1_BASE_URL)
        return resource_map_generator.simple_generate_resource_map(
            resource_map_pid=self.pid, science_metadata_pid=self.metadata_pid,
            science_data_pids=self.resource_pids)

    def _build_system_metadata(self, principal_owner=None):
        acl_set = self._get_package_acl_set(principal_owner=principal_owner)
        d1_sys_meta = dataoneTypes_v2_0.systemMetadata()
        d1_sys_meta.serialVersion = 1
        d1_sys_meta.identifier = self.pid
        d1_sys_meta.size = len(self.resource_map)
        d1_sys_meta.formatId = 'http://www.openarchives.org/ore/terms'
        d1_sys_meta.rightsHolder = properties.DEFAULT_RIGHTS_HOLDER
        d1_sys_meta.checksum = d1_common.checksum.create_checksum_object(
            self.resource_map)
        d1_sys_meta.accessPolicy = self._get_d1_access_policy(acl_set=acl_set)
        return d1_sys_meta

    def _get_package_acl_set(self, principal_owner=None):
        """Return a list of EML access principals and permissions.

        :return: List of access principals and permissions
        """
        auth = (properties.GMN_USER, properties.GMN_PASSWD)
        eml_acl = None
        acl = None

        try:
            r = requests.get(
                self.package.package_purl.replace('/eml/', '/acl/eml/'),
                auth=auth)
            if r.status_code == requests.codes.ok:
                eml_acl = r.text.strip()
        except (requests.exceptions.RequestException,
                requests.exceptions.BaseHTTPError,
                requests.exceptions.HTTPError,
                requests.exceptions.ConnectionError) as e:
            logger.error(e)

        if eml_acl is not None:
            tree = ET.ElementTree(ET.fromstring(eml_acl))
            acl = []
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


def main():
    return 0


if __name__ == "__main__":
    main()
