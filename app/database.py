from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, BigInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Define SQLite database file
DATABASE_URL = "sqlite:///app/database.db"

# Initialize database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Group(Base):
    __tablename__ = 'groups'
    group_id = Column(Integer, primary_key=True, index = True, autoincrement=True)
    groupname = Column(String)
    password = Column(String)

    trips = relationship("Trip", back_populates="group")


class Trip(Base):
    __tablename__ = 'trips'
    trip_id = Column(Integer, primary_key=True, index = True, autoincrement=True)
    tripname = Column(String)
    triptype = Column(String)
    group_id = Column(BigInteger, ForeignKey('groups.group_id'))

    group = relationship("Group", back_populates="trips")
    transactions = relationship("Transaction", back_populates="trip")


class Transaction(Base):
    __tablename__ = 'transactions'
    trans_id = Column(Integer, primary_key=True, index = True, autoincrement=True)
    tr_name = Column(String)
    amount = Column(Float)
    trip_id = Column(BigInteger, ForeignKey('trips.trip_id'))

    trip = relationship("Trip", back_populates="transactions")
    participants = relationship("Participant", back_populates="transaction")


class Participant(Base):
    __tablename__ = 'participants'
    p_id = Column(Integer, primary_key=True, index = True, autoincrement=True)
    name = Column(String)
    is_payer = Column(Boolean)
    trans_id = Column(BigInteger, ForeignKey('transactions.trans_id'))

    transaction = relationship("Transaction", back_populates="participants")


    

# Function to initialize the database
def init_db():
    Base.metadata.create_all(bind=engine)

# Run the initialization if this file is executed
if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")