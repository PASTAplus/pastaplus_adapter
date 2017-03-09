#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: adapter_db

:Synopsis:
    Database model to support queueing objects from PASTA for use by the
    EDI PASTA Adapter and the EDI member node instance of the DataONE GMN.
 
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
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from package import Package

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
        try:
            self.session.add(event)
            self.session.commit()
        except IntegrityError as e:
            logger.error(e)
            self.session.rollback()

    def dequeue(self, event_package=None):
        try:
            event = self.session.query(Queue).filter(
                Queue.package==event_package.get_package_str(),
                Queue.method==event_package.get_method()).one()
            event.dequeued = True
            self.session.commit()
        except NoResultFound as e:
            logger.error('{e} - {package_str}'.format(e=e,
                                package_str=event_package.get_package_str()))

    def get_head(self):
        package = None
        event = self.session.query(Queue).filter(
            Queue.dequeued==False).order_by(Queue.datetime).first()
        if event:
            package = _event_2_package(event=event)
        return package

    def get_last_datetime(self):
        datetime = None
        event = self.session.query(Queue).order_by(desc(Queue.datetime)).first()
        if event:
            datetime = event.datetime.strftime('%Y-%m-%dT%H:%M:%S.%f').rstrip('0')
        return datetime

    def dequeued(self, event_package=None):
        dequeued = None
        try:
            event = self.session.query(Queue).filter(
                Queue.package==event_package.get_package_str(),
                Queue.method==event_package.get_method()).one()
            dequeued = event.dequeued
        except NoResultFound as e:
            logger.error('{e} - {package_str}'.format(e=e,
                            package_str=event_package.get_package_str()))
        return dequeued

def _event_2_package(event=None):
    """Convert a database event record into a Package object.

    :param event: -- the database event record
    :return: -- the Package object
    """
    datetime_str = event.datetime.strftime('%Y-%m-%dT%H:%M:%S.%f').rstrip('0')
    return Package(package_str=event.package, datetime_str=datetime_str,
                   method_str=event.method)

def main():
    return 0


if __name__ == "__main__":
    main()