# tests/dao/test_models.py

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from synopsis.models import *


@pytest.mark.incremental
class TestModels:
    def test_tblhosts_insert_hosts(self, db):
        hosts = [
                Host(name='Server 1', endpoint='127.0.0.1'),
                Host(name='Decommissioned Server', endpoint='192.168.0.253'),
                Host(name='Switch 1', endpoint='192.168.0.129'),
                Host(name='Hub 1', endpoint='192.168.0.1'),
                ]
        db.add_all(hosts)
        db.commit()
        assert db.query(Host).count() == len(hosts)

    def test_tblhosts_delete_host(self, db):
        decom_host = db.query(Host).filter(Host.name.like('Decom%')).first()
        db.delete(decom_host)
        db.commit()
        assert decom_host.id not in [x.id for x in db.query(Host).all()]

    def test_tblhosts_insert_host(self, db):
        db.add(Host(name='Hub 2', endpoint='192.168.0.128'))
        db.commit()
        assert len(db.query(Host).filter(Host.name == 'Hub 2').all()) == 1

    def test_tblhosts_update_host(self, db):
        host = db.query(Host).filter(Host.name == 'Hub 2').first()
        orig = host.endpoint
        host.endpoint = '10.128.1.32'
        db.commit()
        host = db.query(Host).filter(Host.name == 'Hub 2').first()
        assert host.endpoint != orig
        assert host.name == 'Hub 2'

    def test_tblhosts_fail_on_insert_dup_name(self, db):
        count = db.query(Host).count()
        db.add(Host(name='Server 1', endpoint='127.0.0.1'))
        with pytest.raises(IntegrityError) as excinfo:
            db.commit()
        assert 'UNIQUE constraint failed' in str(excinfo.value)
        db.rollback()
        assert count == db.query(Host).count()

    def test_tblhosts_fail_on_insert_null_name(self, db):
        count = db.query(Host).count()
        db.add(Host(name=None, endpoint='1.1.1.1'))
        with pytest.raises(IntegrityError) as excinfo:
            db.commit()
        assert 'NOT NULL constraint failed' in str(excinfo.value)
        db.rollback()
        assert count == db.query(Host).count()

    def test_tblhosts_fail_on_update_to_dup_name(self, db):
        host = db.query(Host).filter(Host.name == 'Hub 2').first()
        host.name = 'Server 1'
        with pytest.raises(IntegrityError) as excinfo:
            db.commit()
        assert 'UNIQUE constraint failed' in str(excinfo.value)

    def test_tblhosts_fail_on_update_to_null_name(self, db):
        host = db.query(Host).filter(Host.name == 'Hub 2').first()
        host.name = None
        with pytest.raises(IntegrityError) as excinfo:
            db.commit()
        assert 'NOT NULL constraint failed' in str(excinfo.value)

    def test_tblhosts_pk_id(self, db):
        hosts = [x.id for x in db.query(Host).all()]
        assert len(hosts) == len(set(hosts))

    def test_tblservices_insert_services(self, db):
        for host in db.query(Host).all():
            db.add_all([
                    Service(host_id=host.id,
                            name='{}_service_1'.format(host.id),
                            alias='Service 1'),
                    Service(host_id=host.id,
                            name='{}_service_2'.format(host.id),
                            alias='Service 2'),
                    Service(host_id=host.id,
                            name='{}_service_3'.format(host.id),
                            alias='Service 3'),
                    ])
        db.commit()
        for host in db.query(Host).all():
            assert db.query(Service).filter(Service.host_id==host.id).count() == 3

    def test_tblservices_insert_service(self, db):
        host = db.query(Host).filter(Host.name == 'Hub 2').first()
        db.add(Service(host_id=host.id, name="decom_service", alias="Decommised Service"))
        db.commit()
        assert db.query(Service).filter(Service.host_id==host.id).count() == 4

    def test_tblsevices_delete_service(self, db):
        service = db.query(Service).filter(Service.name=="decom_service").first()
        db.delete(service)
        db.commit()
        host = db.query(Host).filter(Host.name == 'Hub 2').first()
        assert len(host.services) == 3
