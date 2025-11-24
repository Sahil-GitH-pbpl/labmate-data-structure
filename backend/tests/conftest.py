import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.gettempdir(), "test_infra.db")

from app.main import app  # noqa: E402
from app.db import get_db, SessionLocal  # noqa: E402
from app.models import Base  # noqa: E402


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def setup_database():
    engine = create_engine(os.environ["DATABASE_URL"], connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal.configure(bind=engine)


setup_database()
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
