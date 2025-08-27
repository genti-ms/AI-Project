# Update-Test: 27.08.2025
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
import os



DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sales.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

metadata = Base.metadata

def init_db():
    """
    Create all tables in the database.
    Call this function once on app startup or when you want to create tables.
    """
    metadata.create_all(bind=engine)