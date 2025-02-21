# Dependencies.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://furqan:furqan@localhost:5430/User"
TEST_DATABASE_URL = "sqlite:///./test.db"

# Use SQLite when running tests
import os
if os.getenv("PYTEST_RUNNING") == "true":
    SQLALCHEMY_DATABASE_URL = TEST_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
