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


@lru_cache()
def engine_factory(name):
    return create_engine('sqlite:///:memory:')

@pytest.fixture()
def db():
    engine = engine_factory('simple')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session

