# content of conftest.py

import pytest
import sys

from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from synopsis.models import Base

def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item

def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail("previous test failed (%s)" %previousfailed.name)

@pytest.fixture(scope="class")
def db():
    print(" < db fixture setup")
    engine = create_engine('sqlite:///:memory:')
    #engine = create_engine('sqlite:///a.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    print(" > db fixture teardown")
    session.close()
    engine.dispose()
