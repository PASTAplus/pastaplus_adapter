#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    url = properties.PASTA_URL
    formats = adapter_utilities.get_d1_formats()

    package = qm.get_head()
    while package:
        if  package.is_public(url=url):
            logger.info('Processing: {p}'.format(p=package.get_package_str()))
            resources = package.get_resources(url=url)
            logger.info(resources)
            # for each component:
                # Build system metadata object
            # Build ORE using DOI
            # Determine if create or update
            # Push to GMN
        qm.dequeue(event_package=package)
        package = qm.get_head()

    return 0


if __name__ == "__main__":
    main()
