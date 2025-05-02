import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.database import Base, Group, Trip, Transaction, Participant  # update if your file has a different name

# Use in-memory SQLite for testing (doesn't create actual file)
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="module")
def test_engine():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture(scope="function")
def db_session(test_engine):
    TestingSession = sessionmaker(bind=test_engine)
    session = TestingSession()
    yield session
    session.close()

def test_tables_exist(test_engine):
    inspector = inspect(test_engine)
    tables = inspector.get_table_names()
    assert set(tables) == {"groups", "trips", "transactions", "participants"}

def test_create_group_and_trip(db_session):
    group = Group(groupname="TestGroup", password="1234")
    trip = Trip(tripname="Berlin", triptype=1, group=group)
    db_session.add(group)
    db_session.commit()

    result = db_session.query(Group).filter_by(groupname="TestGroup").first()
    assert result is not None
    assert result.trips[0].tripname == "Berlin"

def test_create_transaction_and_participants(db_session):
    group = Group(groupname="SpendSquad", password="pwd")
    trip = Trip(tripname="TripX", triptype=2, group=group)
    trans = Transaction(tr_name="Dinner", amount=120, trip=trip)
    p1 = Participant(name="Alice", is_payer=True, transaction=trans)
    p2 = Participant(name="Bob", is_payer=False, transaction=trans)

    db_session.add(group)
    db_session.commit()

    saved_trans = db_session.query(Transaction).filter_by(tr_name="Dinner").first()
    assert saved_trans is not None
    assert len(saved_trans.participants) == 2
    assert any(p.name == "Alice" and p.is_payer for p in saved_trans.participants)
