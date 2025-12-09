from flask import Blueprint

# Blueprint for route-related endpoints
route_bp = Blueprint("route_bp", __name__)

from . import (
    routers_create_route,
    routers_create_order,
    routers_optimizations,
    routers_update_order,
    routes_update_route,
    routes_query_route,
    routers_options,
    routes_delete_route,
)
