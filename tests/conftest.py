import pytest
from Delivery_app_BK import create_app
from Delivery_app_BK.models import db
from Delivery_app_BK.models.tables.users_models import Team, User
from Delivery_app_BK.debug_logger import logger, logging

@pytest.fixture
def app():
    app = create_app("testing")
    
    with app.app_context():
        db.create_all() 
        yield app
        db.session.remove()
        db.drop_all() 

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_user(app):
    email = "tester@example.com"
    password = "password123"

    with app.app_context():
        team = Team(name="QA Team")
        user = User(username="tester", email=email, team=team)
        user.password = user.hash_password(password)
        db.session.add_all([team, user])
        db.session.commit()

        return {"email": email, "password": password, "team_id": team.id}


@pytest.fixture
def auth_headers(client, auth_user):
    res = client.post("/auth/login", json={
        "email": auth_user["email"],
        "password": auth_user["password"],
    })
    data = res.get_json()
    token = data["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
def setup_logger():
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger
