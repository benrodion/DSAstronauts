import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, UserGroup, Transaction

# Define a test database URL
TEST_DATABASE_URL = "sqlite:///test_database.db"

# Create a test database engine
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a new database session for testing."""
    Base.metadata.create_all(bind=engine)  # Create tables
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)  # Clean up after test

# Test UserGroup table

def test_create_user_group(db_session):
    user = UserGroup(username="testuser", password="securepassword")
    db_session.add(user)
    db_session.commit()
    
    retrieved_user = db_session.query(UserGroup).filter_by(username="testuser").first()
    assert retrieved_user is not None
    assert retrieved_user.username == "testuser"
    assert retrieved_user.password == "securepassword"

# Test Transaction table

def test_create_transaction(db_session):
    user = UserGroup(username="payeruser", password="password123")
    db_session.add(user)
    db_session.commit()
    
    transaction = Transaction(
        transaction_name="Lunch Payment",
        payer=user.id,
        amount=25.50,
        participants="2,3"
    )
    db_session.add(transaction)
    db_session.commit()
    
    retrieved_transaction = db_session.query(Transaction).filter_by(transaction_name="Lunch Payment").first()
    assert retrieved_transaction is not None
    assert retrieved_transaction.amount == 25.50
    assert retrieved_transaction.payer == user.id
    assert retrieved_transaction.participants == "2,3"

if __name__ == "__main__":
    pytest.main()
