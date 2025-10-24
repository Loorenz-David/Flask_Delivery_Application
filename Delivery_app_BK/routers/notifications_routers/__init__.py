from flask import Blueprint

notifications_bp = Blueprint("notifications_bp", __name__)

from . import routes_create_notifications, routes_update_notifications, routes_query_notifications  # noqa: E402,F401
