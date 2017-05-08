# synopsis/models.py
#
# 
#
#


from sqlalchemy import Table, Column , ForeignKey, Sequence, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

from ._models_utils import assoc_factory

Base = declarative_base()

"""
DATA MODELS
"""

class Host(Base):
    """
    Host data model, this will represent the following:
    Servers, VM Instance, hardware, network device and application
    that has an endpoint(can be reached thru a network connection).
    """
    __tablename__ = 'hosts'
    id = Column(
            Integer,
            Sequence('{}_id_seq'.format(__tablename__)),
            primary_key=True,
            )
    name = Column(String(64), unique=True, nullable=False)
    endpoint = Column(String(128), nullable=False)

    services = relationship("Service", back_populates=__tablename__)

    hostgroups = relationship(
            "HostGroup",
            secondary=assoc_factory(__tablename__, 'hostgroups', Base),
            back_populates=__tablename__,
            )

    def __repr__(self):
        return "Host(id='{}', name='{}', endpoint='{}')".format(
                self.id,
                self.name,
                self.endpoint,
                )


class Service(Base):
    """
    Service data model, this represents a/an attribute/service that is
    being montored on a specified host.
    """
    __tablename__ = 'services'
    id = Column(
            Integer,
            Sequence('{}_id_seq'.format(__tablename__)),
            primary_key=True,
            )
    host_id = Column(Integer, ForeignKey('hosts.id'))
    name = Column(String(64), unique=True, nullable=False)
    alias = Column(String(128), nullable=False)

    hosts = relationship("Host", back_populates=__tablename__)
    servicegroups = relationship(
            "ServiceGroup",
            secondary=assoc_factory(__tablename__, 'servicegroups', Base),
            back_populates=__tablename__,
            )

    def __repr__(self):
        return "Service(id='{}', host_id='{}', name='{}', alias='{}')".format(
                self.id,
                self.host_id,
                self.name,
                self.alias,
                )


class HostGroup(Base):
    """
    Collection of hosts for categorization and organization.
    """
    __tablename__ = 'hostgroups'
    id = Column(
            Integer,
            Sequence('{}_id_seq'.format(__tablename__)),
            primary_key=True,
            )
    name = Column(String(64), unique=True, nullable=False)

    hosts = relationship(
            "Host",
            secondary=assoc_factory(__tablename__, 'hosts', Base),
            back_populates=__tablename__,
            )
    
    def __repr__(self):
        return "HostGroup(id='{}', name='{}')".format(self.id, self.name)


class ServiceGroup(Base):
    """
    Collection of services for categorization and organization.
    """
    __tablename__ = 'servicegroups'
    id = Column(
            Integer,
            Sequence('{}_id_seq'.format(__tablename__)),
            primary_key=True,
            )
    name = Column(String(64), unique=True, nullable=False)

    services = relationship(
            "Service",
            secondary=assoc_factory(__tablename__, 'services', Base),
            back_populates=__tablename__,
            )

    def __repr__(self):
        return "ServiceGroup(id='{}', name='{}')".format(self.id, self.name)
