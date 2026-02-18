from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models.user import User

def test_login_success(client: TestClient, session: Session):
    # Ensure admin exists (created by startup but we dropped tables in conftest?)
    # Wait, conftest drops tables at module teardown, but creates them at module setup.
    # Startup event of app MIGHT NOT RUN when using TestClient(app)!
    # TestClient(app) runs startup events by default (in newer starlette/fastapi).
    # But if startup event runs on `app` (which uses default engine?), and tests use `db_engine` (different connection?).
    # `app` uses `app.db.session.engine`.
    # Tests use `db_engine` from conftest.
    # Using `pool.StaticPool` means in-memory?
    # No, `create_engine(DATABASE_URL)` connects to Postgres.
    # So both connect to same Postgres.
    # If `create_all` runs, tables are empty.
    # Startup runs, creates admin.
    # So admin should exist?
    # Let's verify.
    
    # Create a user manually just in case
    from app.core.security import get_password_hash
    user = User(email="test@example.com", password_hash=get_password_hash("password"), is_active=True)
    session.add(user)
    session.commit()
    
    response = client.post("/api/v1/auth/login", data={"username": "test@example.com", "password": "password"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "session_id" in data

def test_login_failure(client: TestClient):
    response = client.post("/api/v1/auth/login", data={"username": "wrong@example.com", "password": "password"})
    assert response.status_code == 400

def test_magic_link_flow(client: TestClient, session: Session):
    # Request magic link
    email = "test@example.com"
    # Create user first
    from app.core.security import get_password_hash
    user = User(email=email, password_hash=get_password_hash("password"), is_active=True)
    session.add(user)
    session.commit()
    
    response = client.post(f"/api/v1/auth/magic-link?email={email}")
    assert response.status_code == 200
    
    # Get token from DB
    user = session.exec(select(User).where(User.email == email)).first()
    assert user.magic_token is not None
    token = user.magic_token
    
    # Verify
    response = client.get(f"/api/v1/auth/verify?token={token}&email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
