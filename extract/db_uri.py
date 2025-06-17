from sqlalchemy import create_engine

DB_URI = "sqlite:///fundamentals.db"
engine = create_engine(DB_URI)