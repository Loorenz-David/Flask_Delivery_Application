from flask import Blueprint

user_bp = Blueprint("user_bp", __name__)

from . import routes_create_user, routes_update_user, routes_query_user  # noqa: E402,F401
