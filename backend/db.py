# backend/db.py
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from .config import DB_PATH

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

SQLITE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


class Palette(Base):
    __tablename__ = "palettes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), index=True)
    data = Column(Text)  # JSON text


class SessionCanvas(Base):
    __tablename__ = "session_canvases"
    id = Column(Integer, primary_key=True, index=True)
    canvas_id = Column(String(256), index=True)
    user_id = Column(String(256), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    data = Column(Text)  # JSON blob


def init_db():
    """Create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)
