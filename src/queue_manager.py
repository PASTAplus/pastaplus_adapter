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
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from package import Package
import properties

logger = logging.getLogger('adapter_db')

Base = declarative_base()


class Queue(Base):
    __tablename__ = 'queue'

    package = Column(String, primary_key=True)
    scope = Column(String, nullable=False)
    identifier = Column(Integer, nullable=False)
    revision = Column(Integer, nullable=False)
    method = Column(String, primary_key=True)
    datetime = Column(DateTime, nullable=False)
    owner = Column(String, nullable=False)
    doi = Column(String, nullable=False)
    dequeued = Column(Boolean, nullable=False, default=False)


class QueueManager(object):
    def __init__(self, queue=properties.QUEUE):
        self.queue = queue
        db = 'sqlite:///' + self.queue
        engine = create_engine(db)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def delete_queue(self):
        os.remove(self.queue)

    def enqueue(self, event=None):

        scope, identifier, revision = event.package.split('.')

        event = Queue(
            package=event.package,
            scope=scope,
            identifier=identifier,
            revision=revision,
            method=event.method,
            datetime=event.datetime,
            owner=event.owner,
            doi=event.doi
        )
        try:
            self.session.add(event)
            self.session.commit()
        except IntegrityError as e:
            logger.error(e)
            self.session.rollback()

    def dequeue(self, package=None, method=None):
        try:
            event = self.session.query(Queue).filter(
                Queue.package == package,
                Queue.method == method).one()
            event.dequeued = True
            self.session.commit()
        except NoResultFound as e:
            p = package
            logger.error('{e} - {p}'.format(e=e, p=p))

    def get_count(self):
        return self.session.query(func.count(Queue.package)).scalar()

    def get_head(self):
        return self.session.query(Queue).filter(
            Queue.dequeued == False).order_by(Queue.datetime).first()

    def get_last_datetime(self):
        datetime = None
        event = self.session.query(Queue).order_by(desc(Queue.datetime)).first()
        if event is not None:
            datetime = event.datetime
        return datetime

    def is_dequeued(self, package=None, method=None):
        dequeued = None
        try:
            event = self.session.query(Queue).filter(
                Queue.package == package,
                Queue.method == method).one()
            dequeued = event.dequeued
        except NoResultFound as e:
            p = package
            logger.error('{e} - {p}'.format(e=e, p=p))
        return dequeued

    def get_predecessor(self, package=None):
        """
        Return the first predecessor of the event package

        :param event_package: Package instance of event package
        :return: Predecessor as package instance or None if none found
        """
        scope, identifier, revision = package.split('.')
        return self.session.query(Queue).filter(Queue.scope == scope,
                    Queue.identifier == identifier,
                    Queue.revision < revision).order_by(
                    desc(Queue.revision)).first()


def main():
    return 0


if __name__ == "__main__":
    main()
