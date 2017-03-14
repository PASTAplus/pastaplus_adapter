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
import pickle
import os.path
from datetime import datetime
from datetime import timedelta

from d1_client.cnclient_2_0 import CoordinatingNodeClient_2_0

import properties

logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.INFO)

logger = logging.getLogger('adapter_utilities')


def make_https(url=None):
    return url.replace('http:', 'https:', 1)


def make_http(url=None):
    return url.replace('https:', 'http:', 1)


def get_d1_formats(url=properties.D1_BASE_URL):
    """Return dict of D1 formats as pyxb format object.

    Cache formats in "formats.pkl" pickle if D1 listformats()
    fails or if formats is stale based on file modify time.

    :param url: D1 base url
    :return: dict of D1 formats as pyxb format object
    """
    formats_file = '../cache/formats.pkl'
    formats = {}
    if _is_stale_file(filename=formats_file, seconds=3600):
        try:
            cn = CoordinatingNodeClient_2_0(base_url=url)
            format_list = cn.listFormats()
            for _format in format_list.objectFormat:
                formats[_format.formatId] = _format
            fp = open(formats_file, 'wb')
            pickle.dump(formats, file=fp)
        except Exception as e:
            logger.error(e)
    try:
        fp = open(formats_file, 'rb')
        formats = pickle.load(file=fp)
    except IOError as e:
        logger.error(e)
    return formats


def _is_stale_file(filename=None, seconds=None):
    is_stale = False
    try:
        mtime = os.path.getmtime(filename=filename)
        delta = datetime.fromtimestamp(timestamp=mtime) + timedelta(seconds=seconds)
        if delta < datetime.now():
            is_stale = True
    except OSError as e:
        logger.error(e)
        is_stale = True
    return is_stale



def main():

    return 0


if __name__ == "__main__":
    main()
