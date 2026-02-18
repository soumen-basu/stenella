import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel import pool
from app.main import app
from app.api.deps import get_session
from app.core.config import get_settings

settings = get_settings()

@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine(
        settings.DATABASE_URL, 
        poolclass=pool.StaticPool, 
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="session")
def session_fixture(db_engine):
    with Session(db_engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
