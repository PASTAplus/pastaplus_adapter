#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

""":Mod: package_manager

:Synopsis:
 
:Author:
    servilla

:Created:
    3/8/17
"""

import logging
import StringIO

import d1_common
import d1_client.cnclient_2_0
import d1_client.mnclient_2_0
import d1_client.data_package

from queue import QueueManager
from resource import Resource
import properties

logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.INFO)

logger = logging.getLogger('package_manager')


def _make_metadata_url(package_path=None):
    return properties.PASTA_BASE_URL + 'metadata/eml/' + package_path


def _make_package_url(package_path=None):
    return properties.PASTA_BASE_URL + 'eml/' + package_path


def create_gmn_client():
    return d1_client.mnclient_2_0.MemberNodeClient_2_0(
        base_url=properties.GMN_BASE_URL,
        cert_path=properties.GMN_CERT_PATH,
        key_path=properties.GMN_PRIVATE_KEY_PATH,
        timeout=properties.GMN_RESPONSE_TIMEOUT,
    )

def get_predecessor(queue_manager=None, package=None):
    """
    Return first predecessor package that is publicly accessible (some
    predecessors may exist in PASTA, but are not fully public)

    :param queue_manager: queue manager instance for the adapter queue
    :param package: the package instance being processed
    :return: predecessor as a package instance or None if none found
    """
    predecessor = queue_manager.get_predecessor(event_package=package)
    while predecessor and not predecessor.is_public():
        predecessor = queue_manager.get_predecessor(event_package=predecessor)
    return predecessor


def main():
    qm = QueueManager()
    package = qm.get_head()
    while package:
        if package.is_public():
            logger.info('Processing: {p}'.format(p=package.get_package_str()))
            gmn_client = create_gmn_client()
            predecessor = get_predecessor(queue_manager=qm, package=package)
            resources = package.get_resources()
            for resource in resources:
                r = Resource(resource)
                r_sys_meta = r.get_d1_system_metadata(
                    rights_holder=package.get_owner())
                vse_header = r.get_vendor_specific_ext_header()
                if predecessor and r.get_type() == properties.METADATA:
                    old_pid = _make_metadata_url(predecessor.package_path)
                    r_sys_meta.obsoletes = old_pid
                    gmn_client.update(pid=old_pid, obj=StringIO.StringIO(),
                                      newPid=resource, sysmeta=r_sys_meta,
                                      vendorSpecific=vse_header)
                else:
                    gmn_client.create(pid=resource, obj=StringIO.StringIO(),
                                      sysmeta=r_sys_meta,
                                      vendorSpecific=vse_header)
                # Build ORE using DOI
                    # Determine if create or update
                    # lineage = [package.get_package_str()]
                    # predecessor = qm.get_predecessor(event_package=package)
                    # while predecessor:
                    #     lineage.append(predecessor.get_package_str())
                    #     predecessor = qm.get_predecessor(event_package=predecessor)
                    # print(lineage)
                    # Push to GMN
        qm.dequeue(event_package=package)
        package = qm.get_head()

    return 0


if __name__ == "__main__":
    main()
