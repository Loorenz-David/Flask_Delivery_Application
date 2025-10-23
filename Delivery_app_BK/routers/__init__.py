
# Local application imports 
from .auth_routers.token_generation import token_generation_bp
from .item_routers import item_bp
from .order_routers import order_bp
from .route_routers import route_bp

# register all existing blueprints and assign url_prefixes
def register_blueprints( app ):
    app.register_blueprint( token_generation_bp, url_prefix="/auth" )
    app.register_blueprint( item_bp, url_prefix="/item" )
    app.register_blueprint( order_bp, url_prefix="/order" )
    app.register_blueprint( route_bp, url_prefix="/route" )
