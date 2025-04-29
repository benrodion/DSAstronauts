import pytest
from database import Base, engine

@pytest.fixture(autouse=True)
def reset_db():
    # drop all tables
    Base.metadata.drop_all(bind=engine)
    # recreate all tables
    Base.metadata.create_all(bind=engine)
    yield