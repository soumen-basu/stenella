from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models.user import User

def test_read_users_me(client: TestClient, session: Session):
    # Login first
    from app.core.security import get_password_hash
    email = "user@example.com"
    user = User(email=email, password_hash=get_password_hash("password"), is_active=True)
    session.add(user)
    session.commit()
    
    response = client.post("/api/v1/auth/login", data={"username": email, "password": "password"})
    token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == email

def test_update_user_me(client: TestClient, session: Session):
    # Login
    email = "user@example.com"
    # User exists from previous test? Separate module?
    # If separate file, pytest creates new `db_engine` fixture instance?
    # scope="module" means per test file if running `pytest tests/test_users.py`.
    # If running `pytest`, it might share if defined in conftest and scope=session?
    # I defined scope=module. So new DB setup per file.
    # So user DOES NOT exist.
    from app.core.security import get_password_hash
    user = User(email=email, password_hash=get_password_hash("password"), is_active=True)
    session.add(user)
    session.commit()
    
    response = client.post("/api/v1/auth/login", data={"username": email, "password": "password"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Update
    new_name = "New Name"
    response = client.patch("/api/v1/users/me", json={"display_name": new_name}, headers=headers)
    assert response.status_code == 200
    assert response.json()["display_name"] == new_name
    
    # Verify in DB
    session.refresh(user)
    assert user.display_name == new_name
