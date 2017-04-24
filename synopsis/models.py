# synopsis/models.py
#
# 
#
#


from sqlalchemy import Table, Column , ForeignKey, Sequence, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


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
