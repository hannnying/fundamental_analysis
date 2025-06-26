from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Get absolute path to internal/stock_fundamentals.db
BASE_DIR = Path(__file__).resolve().parent
db_path = BASE_DIR / "stock_fundamentals.db"

DATABASE_URL = f"sqlite:///{db_path}"

# Connect to the SQLite database
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# Base class for your models
Base = declarative_base()
