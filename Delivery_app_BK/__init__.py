
# Standard library imports
from datetime import timedelta
import os

# Third-part dependencies
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from Delivery_app_BK.socketio_instance import socketio
from sqlalchemy.orm import configure_mappers


from Delivery_app_BK.routers.utils.compress_request import compress_payload
from Delivery_app_BK.routers.utils.decompress_request import decompress_request



# Local application imports 
from Delivery_app_BK.models import db
from Delivery_app_BK.routers.utils.jwt_handler import jwt


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
    socketio.init_app(app, cors_allowed_origins=frontend_origin)


    from .routers.api_v2 import register_v2_blueprints
    register_v2_blueprints(app)
    from .routers.webhooks import register_webhook_blueprints
    register_webhook_blueprints(app)

    import Delivery_app_BK.sockets.signaling  

    with app.app_context():

        from Delivery_app_BK.services.infra.events import get_event_bus
        get_event_bus()

    configure_mappers()

    
    @app.before_request
    def decompress_response():
        return decompress_request()

    @app.after_request
    def compress_response( response ):

        if request.path.startswith("/api"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        if request.endpoint == "api_v2_integration_shopify.shopify_app_home":
            response.headers["X-Frame-Options"] = "ALLOWALL"
            response.headers["Content-Security-Policy"] = (
                "frame-ancestors https://admin.shopify.com https://*.myshopify.com"
            )
            return response

        compressed_response = compress_payload( response )

        return compressed_response
    

    @app.route("/", methods=["GET"])
    def health():
        return {"status": "ok"}, 200

    return app

