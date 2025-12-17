
# Local application imports 
from .auth_routers.token_generation import token_generation_bp
from .item_routers import item_bp
from .order_routers import order_bp
from .route_routers import route_bp
from .notifications_routers import notifications_bp
from .user_routers import user_bp
from .seed_routers import seed_roles_bp


# register all existing blueprints and assign url_prefixes
def register_blueprints( app ):
    app.register_blueprint( token_generation_bp, url_prefix="/api/auth" )
    app.register_blueprint( item_bp, url_prefix="/api/item" )
    app.register_blueprint( order_bp, url_prefix="/api/order" )
    app.register_blueprint( route_bp, url_prefix="/api/route" )
    app.register_blueprint( notifications_bp, url_prefix="/api/notifications" )
    app.register_blueprint( user_bp, url_prefix="/api/user" )
    app.register_blueprint( seed_roles_bp, url_prefix="/api/seed" )



