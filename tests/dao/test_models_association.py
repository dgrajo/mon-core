# tests/dao/test_models_association.py

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import FlushError
from sqlalchemy.exc import IntegrityError

from synopsis.models import *


@pytest.mark.incremental
class TestModels_Host_HostGroups_Assoc:
    def test_insert_indep(self, db):
        hosts = [
                Host(name='Server 1', endpoint='123.456.789.012'),
                Host(name='Server 2', endpoint='123.012.456.789'),
                Host(name='Server 3', endpoint='123.012.456.781'),
                Host(name='Switch 1', endpoint='123.012.456.1'),
                Host(name='Hub 1', endpoint='123.012.1.1'),
                ]
        groups = [
                HostGroup(name='Hosts'),
                HostGroup(name='Network Device'),
                HostGroup(name='Datacenter A'),
                ]

        db.add_all(hosts + groups) 
        db.commit()
        assert db.query(Host).count() == len(hosts)
        assert db.query(HostGroup).count() == len(groups)

    def test_map_from_hostgroups(self, db):
        group = db.query(HostGroup).filter(HostGroup.name == 'Hosts').first()
        group.hosts.extend(db.query(Host).filter(Host.name.like('Server%')))   
        db.commit()
        group = db.query(HostGroup).filter(HostGroup.name == 'Hosts').first()
        assert 3 == len(group.hosts)
        for host in db.query(Host).filter(Host.name.like('Server%')):
            assert 1 == len(host.hostgroups)

    def test_map_from_hosts(self, db):
        host = db.query(Host).filter(Host.name == 'Switch 1').first()
        host.hostgroups.extend(db.query(HostGroup).filter(HostGroup.name.like('%D%')))
        db.commit()
        for name in ('Network Device', 'Datacenter A'):
            hg = db.query(HostGroup).filter(HostGroup.name == name).first()
            assert len(hg.hosts) == 1

    def test_map_from_hosts_with_dup(self, db):
        group = db.query(HostGroup).filter(HostGroup.name == 'Datacenter A').first()
        group.hosts.extend(db.query(Host).filter(Host.endpoint.like('123.012.456.%')))
        db.commit()
        assert len(group.hosts) == 3

    def test_update_hosts_retain_mapping(self, db):
        host = db.query(Host).filter(Host.name == 'Server 3').first()
        host.name = 'Server'
        db.commit()
        group = db.query(HostGroup).filter(HostGroup.name == 'Datacenter A').first()
        assert host.name in [x.name for x in group.hosts]

    def test_update_hostgroups_retain_mapping(self, db):
        group = db.query(HostGroup).filter(HostGroup.name == 'Network Device').first()
        group.name = 'network devices'
        db.commit()
        assert group.name in [x.name for x in db.query(Host).filter(Host.name == 'Switch 1').first().hostgroups]

    def test_delete_host_reflect(self, db):
        host = db.query(Host).filter(Host.name == 'Server').first()
        db.delete(host)
        db.commit()
        assert host.name not in [x.name for x in db.query(HostGroup).filter(HostGroup.name == 'Datacenter A').first().hosts]

    def test_disassociate_host(self, db):
        host = db.query(Host).filter(Host.name == 'Switch 1').first()
        group = db.query(HostGroup).filter(HostGroup.name == 'Datacenter A').first()
        group_count = len(group.hosts)
        host.hostgroups.remove(group)
        db.commit()
        assert (group_count - len(group.hosts)) == 1

    def test_associate_null_hostgroups(self, db):
        group = db.query(HostGroup).filter(HostGroup.name == 'Hosts').first()
        group.hosts.append(None)
        with pytest.raises(FlushError) as excinfo:
            db.commit()
        assert "Can't flush None value" in str(excinfo.value)
        db.rollback()

    def test_associate_null_hosts(self, db):
        host = db.query(Host).filter(Host.name == 'Hub 1').first()
        host.hostgroups.append(None)
        with pytest.raises(FlushError) as excinfo:
            db.commit()
        assert "Can't flush None value" in str(excinfo.value)
        db.rollback()


@pytest.mark.incremental
class TestModels_Service_ServiceGroups_Assoc:
    def test_insert_indep(self, db):
        hosts = [
                Host(name='Server 1', endpoint='123.456.789.012'),
                ]
        groups = [
                ServiceGroup(name='Critical'),
                ServiceGroup(name='Major'),
                ServiceGroup(name='Minor'),
                ]

        db.add_all(hosts + groups) 

        for host in db.query(Host).all():
            db.add_all([
                    Service(host_id=host.id,
                            name='{}_critical'.format(host.id),
                            alias='Critical Service'),
                    Service(host_id=host.id,
                            name='{}_major'.format(host.id),
                            alias='Major Service'),
                    Service(host_id=host.id,
                            name='{}_minor'.format(host.id),
                            alias='Minor Service'),
                    ])
        db.commit()

        assert db.query(Host).count() == len(hosts)
        assert db.query(ServiceGroup).count() == len(groups)
        assert db.query(Service).count() == 3

    def test_map_from_servicegroups(self, db):
        for group in db.query(ServiceGroup).all():
            group.services.extend(db.query(Service).filter(Service.name.like('%{}%'.format(group.name.lower()))))
        db.commit()

        for group in db.query(ServiceGroup).all():
            service = db.query(Service).filter(Service.name.like('%{}%'.format(group.name.lower()))).first()
            assert service in group.services

    def test_map_from_services(self, db):
        for group in db.query(ServiceGroup).all():
            service = db.query(Service).filter(Service.name.like('%{}%'.format(group.name.lower()))).first()
            assert group in service.servicegroups
"""
    def test_map_from_hosts_with_dup(self, db):
        group = db.query(HostGroup).filter(HostGroup.name == 'Datacenter A').first()
        group.hosts.extend(db.query(Host).filter(Host.endpoint.like('123.012.456.%')))
        db.commit()
        assert len(group.hosts) == 3

    def test_update_hosts_retain_mapping(self, db):
        host = db.query(Host).filter(Host.name == 'Server 3').first()
        host.name = 'Server'
        db.commit()
        group = db.query(HostGroup).filter(HostGroup.name == 'Datacenter A').first()
        assert host.name in [x.name for x in group.hosts]

    def test_update_hostgroups_retain_mapping(self, db):
        group = db.query(HostGroup).filter(HostGroup.name == 'Network Device').first()
        group.name = 'network devices'
        db.commit()
        assert group.name in [x.name for x in db.query(Host).filter(Host.name == 'Switch 1').first().hostgroups]

    def test_delete_host_reflect(self, db):
        host = db.query(Host).filter(Host.name == 'Server').first()
        db.delete(host)
        db.commit()
        assert host.name not in [x.name for x in db.query(HostGroup).filter(HostGroup.name == 'Datacenter A').first().hosts]

    def test_disassociate_host(self, db):
        host = db.query(Host).filter(Host.name == 'Switch 1').first()
        group = db.query(HostGroup).filter(HostGroup.name == 'Datacenter A').first()
        group_count = len(group.hosts)
        host.hostgroups.remove(group)
        db.commit()
        assert (group_count - len(group.hosts)) == 1

    def test_associate_null_hostgroups(self, db):
        group = db.query(HostGroup).filter(HostGroup.name == 'Hosts').first()
        group.hosts.append(None)
        with pytest.raises(FlushError) as excinfo:
            db.commit()
        assert "Can't flush None value" in str(excinfo.value)
        db.rollback()

    def test_associate_null_hosts(self, db):
        host = db.query(Host).filter(Host.name == 'Hub 1').first()
        host.hostgroups.append(None)
        with pytest.raises(FlushError) as excinfo:
            db.commit()
        assert "Can't flush None value" in str(excinfo.value)
        db.rollback()
"""