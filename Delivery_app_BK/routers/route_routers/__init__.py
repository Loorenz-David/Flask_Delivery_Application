from flask import Blueprint

# Blueprint for route-related endpoints
route_bp = Blueprint("route_bp", __name__)

from . import (
    routers_create_route,
    routers_optimizations,
    routes_update_route,
    routes_query_route,
    routers_options,
    routes_delete_route,
)
