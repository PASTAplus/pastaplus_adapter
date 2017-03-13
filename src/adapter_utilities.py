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
    """Return dict of D1 formats as pyxb format object

    Cache formats in "formats.pkl" pickle if D1 listformats()
    fails.

    :param url: D1 base url
    :return: dict of D1 formats as pyxb format object
    """
    formats = {}
    try:
        cn = CoordinatingNodeClient_2_0(base_url=url)
        format_list = cn.listFormats()
        for format in format_list.objectFormat:
            formats[format.formatId] = format
        fp = open('formats.pkl', 'wb')
        pickle.dump(formats, file=fp)
    except Exception as e:
        logger.error(e)
        fp = open('formats.pkl', 'rb')
        formats = pickle.load(file=fp)

    return formats

def main():

    return 0


if __name__ == "__main__":
    main()
