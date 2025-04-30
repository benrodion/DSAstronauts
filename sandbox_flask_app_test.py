import pytest
from pytest_mock import MockFixture
from sandbox_flask_app import app, Group
from database import SessionLocal
import bcrypt

@pytest.fixture
def client():
    app.config.update({"TESTING": True})

    with app.test_client() as client:
        yield client


def test_show_login_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Your @group_name" in response.data

def test_show_login_page_missing_groupname(client):
    no_group_response = client.post("/", data={
        "loggroupid": "", 
        "logpass": "Password"})
    
    no_password_response = client.post("/", data={
        "loggroupid": "Bensgroup", 
        "logpass": ""})

    assert b"Group name missing" in no_group_response.data
    assert b"Password missing" in no_password_response.data

def test_login_invalid_creds(client):
    # no user in the database -> should be invalid
    invalid_user_response = client.post("/", data={
        "loggroupid": "Girlstrip", "logpass": "Password"})
    
    assert b"Invalid username or password" in invalid_user_response.data

def test_login_valid_creds(client):

    # add a user
    db = SessionLocal()
    pw = bcrypt.hashpw(b"secret", bcrypt.gensalt()).decode()
    db.add(Group(groupname="team1", password=pw))
    db.commit()
    db.close()

    valid_user_response = client.post("/", data={"loggroupid": "team1", "logpass": "secret"})
    r2 = client.get("/dashboard") # follow the redirect

    assert valid_user_response.status_code == 302 # should redirect
    assert b"Girl Math" in r2.data # did we land on the dashboard?

def test_signup(client):
    valid_response = client.post("/signup", data={
        "newloggroupid": "Monasgroup",
        "newlogpass": "Password",
    })

    same_username_response = client.post("/signup", data={
        "newloggroupid": "Monasgroup",
        "newlogpass": "Password123",
    })

    invalid_response = client.post("/signup", data={
        "newloggroupid": "",
        "newlogpass": "Password",
    })

    bad_password_response = client.post("/signup", data={
        "newloggroupid": "Sofiyasgroup",
        "newlogpass": "pw",
    })

    assert valid_response.status_code == 200
    assert b"Sign-up successful!" in valid_response.data
    assert b"Username already exists" in same_username_response.data
    assert b"Username or password missing" in invalid_response.data
    assert b"Password must be at least 4 characters." in bad_password_response.data