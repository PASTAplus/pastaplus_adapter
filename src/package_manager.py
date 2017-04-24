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

import os
import logging

# Set level to WARN to avoid verbosity in requests at INFO
logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.WARN)
import StringIO

import d1_client.cnclient_2_0
import d1_client.mnclient_2_0
import d1_client.data_package

from queue_manager import QueueManager
from resource import Resource
from resource_map import ResourceMap
from lock import Lock
import properties

logger = logging.getLogger('package_manager')


def make_metadata_url(package_path=None):
    return properties.PASTA_BASE_URL + 'metadata/eml/' + package_path


def make_package_url(package_path=None):
    return properties.PASTA_BASE_URL + 'eml/' + package_path


def create_gmn_client():
    return d1_client.mnclient_2_0.MemberNodeClient_2_0(
        base_url=properties.GMN_BASE_URL,
        cert_pem_path=properties.GMN_CERT_PATH,
        cert_key_path=properties.GMN_PRIVATE_KEY_PATH,
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


def is_metadata(resource=None):
    return resource.get_type() == properties.METADATA


def main():

    lock = Lock('/tmp/package_manager.lock')
    if lock.locked:
        logger.error('Lock file {} exists, exiting...'.format(lock.lock_file))
        return 1
    else:
        lock.acquire()
        logger.warn('Lock file {} acquired'.format(lock.lock_file))

    qm = QueueManager()
    package = qm.get_head()
    gmn_client = create_gmn_client()
    while package is not None:
        logger.warn('Active package: {p}'.format(p=package.package_str))
        if package.is_public():
            logger.warn('Processing: {p}'.format(p=package.package_str))
            if package.get_method() in [properties.CREATE, properties.UPDATE]:
                predecessor = get_predecessor(queue_manager=qm, package=package)
                resources = package.get_resources()
                po = package.get_owner()
                logger.info(resources)
                # TODO: get scimeta resource
                # TODO: process and check for D1 code in additionalMetadata
                # TODO: remove from resource list
                for resource in resources:
                    r = Resource(resource)
                    sysmeta = r.get_d1_sysmeta(principal_owner=po)
                    header = r.get_vendorSpecific_header()
                    if predecessor and is_metadata(resource=r):
                        old_pid = make_metadata_url(
                            predecessor.package_path)
                        sysmeta.obsoletes = old_pid
                        logger.warn('Update: {}<-{}'.format(old_pid, resource))
                        try:
                            gmn_client.update(pid=old_pid,
                                              obj=StringIO.StringIO(),
                                              newPid=resource,
                                              sysmeta_pyxb=sysmeta,
                                              vendorSpecific=header)
                        except Exception as e:
                            logger.error(e)
                    else:
                        logger.warn('Create: {}'.format(resource))
                        try:
                            gmn_client.create(pid=resource,
                                              obj=StringIO.StringIO(),
                                              sysmeta_pyxb=sysmeta,
                                              vendorSpecific=header)
                        except Exception as e:
                            logger.error(e)
                resource_map = ResourceMap(package=package)
                sysmeta = resource_map.get_resource_map_system_metadata()
                rmap = resource_map.get_resource_map()
                resource_map_pid = resource_map.get_resource_map_pid()
                if predecessor:
                    predecessor_pid = predecessor.get_doi()
                    if predecessor_pid is None:
                        predecessor_pid = predecessor.get_package_purl()
                    old_pid = predecessor_pid
                    sysmeta.obsoletes = old_pid
                    logger.warn('Update: {}<-{}'.format(old_pid,
                                                        resource_map_pid))
                    try:
                        gmn_client.update(pid=old_pid,
                                          obj=StringIO.StringIO(rmap),
                                          newPid=resource_map_pid,
                                          sysmeta_pyxb=sysmeta)
                    except Exception as e:
                        logger.error(e)
                else:
                    logger.warn('Create: {}'.format(resource_map_pid))
                    try:
                        gmn_client.create(pid=resource_map_pid,
                                          obj=StringIO.StringIO(rmap),
                                          sysmeta_pyxb=sysmeta)
                    except Exception as e:
                        logger.error(e)

            else:  # deleteDataPackage
                resources = package.get_resources()
                for resource in resources:
                    logger.warn('Delete: {}'.format(resource))
                    try:
                        gmn_client.archive(pid=resource)
                    except Exception as e:
                        logger.error(e)
                pid = package.get_doi()
                logger.warn('Delete: {}'.format(pid))
                try:
                    gmn_client.archive(pid=pid)
                except Exception as e:
                    logger.error(e)
        else:
            logger.warn('Package {p} is not public'.format(
                                                    p=package.package_str))
        qm.dequeue(event_package=package)
        package = qm.get_head()

    logger.warn('Queue empty')
    lock.release()
    logger.warn('Lock file {} released'.format(lock.lock_file))
    return 0


if __name__ == "__main__":
    main()
