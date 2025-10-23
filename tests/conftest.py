import pytest
from Delivery_app_BK import create_app, debug_logger
from Delivery_app_BK.models import db
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


@pytest.fixture(autouse=True)
def setup_logger():
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger