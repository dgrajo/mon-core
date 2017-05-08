# tests/dao/test_models.py

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from synopsis.models import *


@pytest.mark.incremental
class TestModelHost:

    #
    # `hosts` table requirements tests
    #

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
        assert host.endpoint == '10.128.1.32'
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
        db.rollback()

    def test_tblhosts_fail_on_update_to_null_name(self, db):
        host = db.query(Host).filter(Host.name == 'Hub 2').first()
        host.name = None
        with pytest.raises(IntegrityError) as excinfo:
            db.commit()
        assert 'NOT NULL constraint failed' in str(excinfo.value)
        db.rollback()

    def test_tblhosts_pk_id(self, db):
        hosts = [x.id for x in db.query(Host).all()]
        assert len(hosts) == len(set(hosts))


class TestModelService:
    #
    # `services` table requirements tests
    #

    def test_tblservices_insert_services(self, db):
        hosts = [
                Host(name='Server 1', endpoint='127.0.0.1'),
                Host(name='Hub 2', endpoint='10.54.75.1'),
                ]
        db.add_all(hosts)
        db.commit()
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

    def test_tblservices_delete_service(self, db):
        service = db.query(Service).filter(Service.name=="decom_service").first()
        db.delete(service)
        db.commit()
        host = db.query(Host).filter(Host.name == 'Hub 2').first()
        assert len(host.services) == 3
        assert service.id not in [x.id for x in db.query(Service).all()]

    def test_tblservices_update_service(self,db):
        host = db.query(Host).filter(Host.name == 'Hub 2').first()
        db.add(Service(host_id=host.id, name="updated_service", alias="Updated Service"))
        db.commit()
        service = db.query(Service).filter(Service.name=="updated_service").first()
        service.name = "updated_service_0"
        service.alias = "Service Updated"
        service.host_id = db.query(Host).filter(Host.name == "Server 1").first().id
        db.commit()
        q_service = db.query(Service).filter(Service.name == 'updated_service_0').first()
        assert q_service.host_id == service.host_id
        assert q_service.name == service.name
        assert q_service.alias == service.alias

    def test_tblservices_fail_on_insert_dup_name(self, db):
        host = db.query(Host).filter(Host.name == 'Hub 2').first()
        db.add(Service(host_id=host.id, name="updated_service_0", alias="Service Updated"))
        with pytest.raises(IntegrityError) as excinfo:
            db.commit()
        assert 'UNIQUE constraint failed' in str(excinfo.value)
        db.rollback()

    def test_tblservices_fail_on_insert_null_name(self, db):
        host = db.query(Host).filter(Host.name == 'Hub 2').first()
        db.add(Service(host_id=host.id, name=None, alias="Service Updated"))
        with pytest.raises(IntegrityError) as excinfo:
            db.commit()
        assert 'NOT NULL constraint failed' in str(excinfo.value)
        db.rollback()
        
    def test_tblservices_fail_on_update_dup_name(self, db):
        service = db.query(Service).filter(Service.name == 'updated_service_0').first()
        service.name = '1_service_1'
        with pytest.raises(IntegrityError) as excinfo:
            db.commit()
        assert 'UNIQUE constraint failed' in str(excinfo.value)
        db.rollback()
        
    def test_tblservices_fail_on_update_null_name(self, db):
        service = db.query(Service).filter(Service.name == 'updated_service_0').first()
        service.name = None
        with pytest.raises(IntegrityError) as excinfo:
            db.commit()
        assert 'NOT NULL constraint failed' in str(excinfo.value)
        db.rollback()
        
    def test_tblservice_pk_id(self, db):
        service = [x.id for x in db.query(Service).all()]
        assert len(service) == len(set(service))

class TestModelHostGroups:
    #
    # `hostgroups` table requirements tests
    #

    def test_tblhostgroups_insert_hostgroups(self, db):
        hostgroups = [
                HostGroup(name='Host Servers'),
                HostGroup(name='Network device'),
                HostGroup(name='Virtual hosts'),
                ]
        db.add_all(hostgroups)
        db.commit()
        assert len(hostgroups) == db.query(HostGroup).count()
        assert hostgroups[1] == db.query(HostGroup).all()[1]

    def test_tblhostgroups_insert_hostgroup(self, db):
        db.add(HostGroup(name='Old host group'))
        db.commit()
        assert db.query(HostGroup).count() == 4
        assert db.query(HostGroup).filter(HostGroup.name == 'Old host group').first() != None

    def test_tblhostgroups_update_hostgroup(self, db):
        hostgroup = db.query(HostGroup).filter(HostGroup.name == 'Old host group').first()
        hostgroup.name = 'old hostgroup'
        db.commit()
        assert hostgroup.id == db.query(HostGroup).filter(HostGroup.name == 'old hostgroup').first().id

    def test_tblhostgroups_delete_hostgroup(self, db):
        hostgroup = db.query(HostGroup).filter(HostGroup.name == 'old hostgroup').first()
        db.delete(hostgroup)
        db.commit()
        assert hostgroup.id not in [x.id for x in db.query(HostGroup).all()] 
        assert db.query(HostGroup).count() == 3

    def test_tblhostgroups_fail_on_insert_dup_name(self, db):
        db.add(HostGroup(name='Host Servers'))
        with pytest.raises(IntegrityError) as excinfo:
            db.commit()
        assert 'UNIQUE constraint failed' in str(excinfo.value)
        db.rollback()
        
    def test_tblhostgroups_fail_on_insert_null_name(self, db):
        db.add(HostGroup(name=None))
        with pytest.raises(IntegrityError) as excinfo:
            db.commit()
        assert 'NOT NULL constraint failed' in str(excinfo.value)
        db.rollback()

    def test_tblhostgroups_fail_on_update_dup_name(self, db):
        hostgroup = db.query(HostGroup).filter(HostGroup.name == 'Network device').first()
        hostgroup.name = 'Host Servers'
        with pytest.raises(IntegrityError) as excinfo:
            db.commit()
        assert 'UNIQUE constraint failed' in str(excinfo.value)
        db.rollback()

    def test_tblhostgroups_fail_on_update_null_name(self, db):
        hostgroup = db.query(HostGroup).filter(HostGroup.name == 'Network device').first()
        hostgroup.name = None
        with pytest.raises(IntegrityError) as excinfo:
            db.commit()
        assert 'NOT NULL constraint failed' in str(excinfo.value)
        db.rollback()

class TestModelServiceGroups:
    """
    `servicegroups` table requirements tests
    """
    def test_tblhostgroups_insert_hostgroups(self, db):
        hostgroups = [
                HostGroup(name='Host Servers'),
                HostGroup(name='Network device'),
                HostGroup(name='Virtual hosts'),
                ]
        db.add_all(hostgroups)
        db.commit()
        assert len(hostgroups) == db.query(HostGroup).count()
        assert hostgroups[1] == db.query(HostGroup).all()[1]

    def test_tblhostgroups_insert_hostgroup(self, db):
        db.add(HostGroup(name='Old host group'))
        db.commit()
        assert db.query(HostGroup).count() == 4
        assert db.query(HostGroup).filter(HostGroup.name == 'Old host group').first() != None

    def test_tblhostgroups_update_hostgroup(self, db):
        hostgroup = db.query(HostGroup).filter(HostGroup.name == 'Old host group').first()
        hostgroup.name = 'old hostgroup'
        db.commit()
        assert hostgroup.id == db.query(HostGroup).filter(HostGroup.name == 'old hostgroup').first().id

    def test_tblhostgroups_delete_hostgroup(self, db):
        hostgroup = db.query(HostGroup).filter(HostGroup.name == 'old hostgroup').first()
        db.delete(hostgroup)
        db.commit()
        assert hostgroup.id not in [x.id for x in db.query(HostGroup).all()]
        assert db.query(HostGroup).count() == 3

    def test_tblhostgroups_fail_on_insert_dup_name(self, db):
        db.add(HostGroup(name='Host Servers'))
        with pytest.raises(IntegrityError) as excinfo:
            db.commit()
        assert 'UNIQUE constraint failed' in str(excinfo.value)
        db.rollback()

    def test_tblhostgroups_fail_on_insert_null_name(self, db):
        db.add(HostGroup(name=None))
        with pytest.raises(IntegrityError) as excinfo:
            db.commit()
        assert 'NOT NULL constraint failed' in str(excinfo.value)
        db.rollback()

    def test_tblhostgroups_fail_on_update_dup_name(self, db):
        hostgroup = db.query(HostGroup).filter(HostGroup.name == 'Network device').first()
        hostgroup.name = 'Host Servers'
        with pytest.raises(IntegrityError) as excinfo:
            db.commit()
        assert 'UNIQUE constraint failed' in str(excinfo.value)
        db.rollback()

    def test_tblhostgroups_fail_on_update_null_name(self, db):
        hostgroup = db.query(HostGroup).filter(HostGroup.name == 'Network device').first()
        hostgroup.name = None
        with pytest.raises(IntegrityError) as excinfo:
            db.commit()
        assert 'NOT NULL constraint failed' in str(excinfo.value)
        db.rollback()
