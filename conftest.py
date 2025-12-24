import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import table_registry
from main import app
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:")
    table_registry.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)
