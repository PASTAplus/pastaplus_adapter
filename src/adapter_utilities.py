#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: adapter_utilities

:Synopsis:
 
:Author:
    servilla

:Created:
    3/8/17
"""

import logging

logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.INFO)

logger = logging.getLogger('adapter_utilities')


def makeHttps(url=None):
    return url.replace('http:', 'https:', 1)


def main():
    return 0


if __name__ == "__main__":
    main()