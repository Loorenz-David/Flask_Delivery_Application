import pytest
from Delivery_app_BK import create_app, debug_logger
from Delivery_app_BK.models import db

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