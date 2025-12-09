from flask import Blueprint

user_bp = Blueprint("user_bp", __name__)

from . import route_register_user, routes_create_user, routes_update_user, routes_query_user, routes_delete_user  # noqa: E402,F401
