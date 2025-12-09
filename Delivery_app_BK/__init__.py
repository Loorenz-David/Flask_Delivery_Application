# Standard library imports
from datetime import timedelta
import os

# Third-part dependencies
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate





# Local application imports 
from Delivery_app_BK.models import db
from Delivery_app_BK.routers.auth_routers.utils.jwt_handler import jwt


# configuration map
config_map = {
    "development": "Delivery_app_BK.config.development.DevelopmentConfig",
    "testing": "Delivery_app_BK.config.testing.TestingConfig",
    "production": "Delivery_app_BK.config.production.ProductionConfig",
}



# app factory
def create_app(config_name="development"):

    app = Flask(__name__)
    
    # app configuration
    app.config.from_object(config_map.get(config_name))

    frontend_origin = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")
    CORS(app, resources={r"/*": {"origins": frontend_origin}}, supports_credentials=True)

    # init app object
    db.init_app(app)
    jwt.init_app(app)

    Migrate(app, db)

    from .routers import register_blueprints
    register_blueprints(app)

    if config_name == 'development':
        with app.app_context():
            db.create_all()

            

    return app





