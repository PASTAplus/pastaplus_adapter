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
from sqlalchemy import create_engine

import package

Base = declarative_base()
logger = logging.getLogger('adapter_db')


class Queue(Base):

    __tablename__ = 'queue'

    package = Column(String, primary_key=True)
    scope = Column(String, nullable=False)
    identifier = Column(Integer, nullable=False)
    revision = Column(Integer, nullable=False)
    method = Column(String, primary_key=True)
    datetime = Column(DateTime, nullable=False)
    dequeued = Column(Boolean, nullable=False, default=False)


class QueueManager(object):

    def __init__(self, queue='adapter_queue.sqlite'):
        os.chdir('../db')
        cwd = os.getcwd()
        self.db_path = cwd + '/' + queue
        db = 'sqlite:///' + self.db_path
        engine = create_engine(db)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def delete_queue(self):
        os.remove(self.db_path)

    def enqueue(self, event_package=None):
        event = Queue(
            package = event_package.get_package_str(),
            scope = event_package.get_scope(),
            identifier = event_package.get_identifier(),
            revision = event_package.get_revision(),
            method = event_package.get_method(),
            datetime = event_package.get_datetime()
        )

        self.session.add(event)
        self.session.commit()

    def get_head(self):
        pass

    def get_all(self):
        return self.session.query(Queue).all()

    def dequeue(self, event_package=None):
        pass

    def get_last_event(self):
        pass

def main():
    return 0


if __name__ == "__main__":
    main()