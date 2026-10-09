import os, tempfile
import pytest
import app as module

@pytest.fixture()
def client(monkeypatch):
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    monkeypatch.setattr(module, "DB_PATH", tmp.name)
    module.FAILURES.clear()
    module.init_db()
    module.app.config.update(TESTING=True, SECRET_KEY="test-secret")
    with module.app.test_client() as client:
        yield client
    os.unlink(tmp.name)

def test_home_loads(client):
    assert client.get("/").status_code == 200

def test_registration_rejects_weak_password(client):
    response = client.post("/register", data={
        "username": "newuser", "email": "newuser@example.test", "password": "password123"
    })
    assert response.status_code == 200
    assert b"at least 12 characters" in response.data or b"denylist" in response.data

def test_user_cannot_access_admin(client):
    # A direct route guard check without needing to complete MFA.
    with client.session_transaction() as sess:
        sess["user_id"] = 2
        sess["username"] = "alice"
        sess["role"] = "USER"
    assert client.get("/admin").status_code == 403

def test_password_hash_is_not_plaintext(client):
    with module.db() as conn:
        row = conn.execute("SELECT password_hash FROM users WHERE username='alice'").fetchone()
    assert row["password_hash"] != "ChangeMe-User-2026!"
    assert row["password_hash"].startswith("scrypt:")
