#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: adapter_db

:Synopsis:
 
:Author:
    servilla

:Created:
    3/2/17
"""

import os
import logging

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
logger = logging.getLogger('adapter_db')

class AdapterDb(Base):

    __tablename__ = 'adapter_db'

    package = Column(String, primary_key=True)
    scope = Column(String, nullable=False)
    identifier = Column(Integer, nullable=False)
    revision = Column(Integer, nullable=False)
    datetime = Column(DateTime, nullable=False)
    dequeued = Column(Boolean, nullable=False, default=False)



def main():
    return 0


if __name__ == "__main__":
    main()