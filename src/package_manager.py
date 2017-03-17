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

from queue import QueueManager
from package import Package
import adapter_utilities
import properties


logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.INFO)

logger = logging.getLogger('package_manager')


def main():
    qm = QueueManager()
    url = properties.PASTA_BASE_URL
    formats = adapter_utilities.get_d1_formats()

    package = qm.get_head()
    while package:
        if package.is_public():
            logger.info('Processing: {p}'.format(p=package.get_package_str()))
            resources = package.get_resources()
            logger.info(resources)
            # for each resource:
                # Build system metadata object
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
