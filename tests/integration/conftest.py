from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.database import SessionLocal
from app.main import app
from app.models import Book


@pytest.fixture(autouse=True)
def clean_database() -> Iterator[None]:
    with SessionLocal() as session:
        session.execute(delete(Book))
        session.commit()

    yield

    with SessionLocal() as session:
        session.execute(delete(Book))
        session.commit()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
