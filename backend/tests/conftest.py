import os
import tempfile

import pytest
from sqlalchemy import create_engine

from app.auth.arpra_jwt import User
from app.db import SessionLocal
from app.models import Base


os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.gettempdir(), "test_infra.db")


def setup_database():
    engine = create_engine(os.environ["DATABASE_URL"], connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal.configure(bind=engine)


setup_database()


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def users():
    return {
        "alice": User(username="alice", role="Staff", department="Operations"),
        "bob": User(username="bob", role="IT", department="IT"),
        "admin": User(username="admin", role="Admin", department="Admin"),
    }
