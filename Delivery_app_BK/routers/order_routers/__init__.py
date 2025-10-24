from flask import Blueprint

# Blueprint for order-related endpoints
order_bp = Blueprint("order_bp", __name__)

from . import routers_create_order, routes_update_order, routes_query_order
