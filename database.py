from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Define SQLite database file
DATABASE_URL = "sqlite:///database.db"

# Initialize database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define User Groups table
class UserGroup(Base):
    __tablename__ = "user_groups"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

# Define Transactions table
class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    transaction_name = Column(String, nullable=False)
    payer = Column(Integer, ForeignKey("user_groups.id"), nullable=False)
    amount = Column(Float, nullable=False)
    participants = Column(String, nullable=False)  # Store participant IDs as comma-separated values

    payer_user = relationship("UserGroup")

# Function to initialize the database
def init_db():
    Base.metadata.create_all(bind=engine)

# Run the initialization if this file is executed
if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")