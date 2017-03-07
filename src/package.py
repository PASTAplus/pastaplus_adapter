#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: package

:Synopsis:
 
:Author:
    servilla

:Created:
    3/2/17
"""

from datetime import datetime

import logging

logger = logging.getLogger('package')


class Package(object):

   def __init__(self, package_str=None, datetime_str=None, method_str=None):
       self.package_str = package_str.strip()
       self.package = self.package_str.split(".")
       self.scope = self.package[0].strip()
       self.identifier = int(self.package[1])
       self.revision = int(self.package[2])

       if 'T' in datetime_str:
           self.datetime = datetime.strptime(datetime_str,
                                             '%Y-%m-%dT%H:%M:%S.%f')
       else:
           self.datetime = datetime.strptime(datetime_str,
                                             '%Y-%m-%d %H:%M:%S.%f')

       self.method = method_str.strip()

   def get_package_str(self):
       return self.package_str

   def get_scope(self):
       return self.scope

   def get_identifier(self):
       return self.identifier

   def get_revision(self):
       return self.revision

   def get_datetime(self):
       return self.datetime

   def get_method(self):
       return self.method


def main():
    return 0


if __name__ == "__main__":
    main()