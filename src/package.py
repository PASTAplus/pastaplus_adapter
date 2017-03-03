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

   def __init__(self, package=None):
       self.package = package.split(".")
       self.scope = self.package[0].strip()
       self.identifier = int(self.package[1].strip())
       self.revision = int(self.package[2].strip())

   def set_datetime(self, datetime_str=None):
       self.datetime = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f')


   def get_package(self):
       return self.scope + '.' + str(self.identifier) + '.' + str(self.revision)

   def get_scope(self):
       return self.scope

   def get_identifier(self):
       return self.identifier

   def get_revision(self):
       return self.revision

   def get_datetime(self):
       return self.datetime


def main():
    return 0


if __name__ == "__main__":
    main()