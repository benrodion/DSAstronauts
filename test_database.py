from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Define SQLite database file
DATABASE_URL = "sqlite:///database.db"

# Initialize database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Groups Table
class Group(Base):
    __tablename__ = "groups"
    group_id = Column(Integer, primary_key=True, autoincrement=True)
    groupname = Column(String, nullable=False)
    password = Column(String, nullable=False)

    trips = relationship("Trip", back_populates="group")

# Trips Table
class Trip(Base):
    __tablename__ = "trips"
    trip_id = Column(Integer, primary_key=True, autoincrement=True)
    tripname = Column(String, nullable=False)
    triptype = Column(Integer, nullable=False)
    group_id = Column(Integer, ForeignKey("groups.group_id"))

    group = relationship("Group", back_populates="trips")
    transactions = relationship("Transaction", back_populates="trip")

# Transactions Table
class Transaction(Base):
    __tablename__ = "transactions"
    trans_id = Column(Integer, primary_key=True, autoincrement=True)
    tr_name = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    trip_id = Column(Integer, ForeignKey("trips.trip_id"))

    trip = relationship("Trip", back_populates="transactions")
    participants = relationship("Participant", back_populates="transaction")

# Participants Table
class Participant(Base):
    __tablename__ = "participants"
    p_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    is_payer = Column(Boolean, nullable=False)
    trans_id = Column(Integer, ForeignKey("transactions.trans_id"))

    transaction = relationship("Transaction", back_populates="participants")

# Function to initialize the database
def init_db():
    Base.metadata.create_all(bind=engine)

# Run the initialization if this file is executed
if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
