from flask import Blueprint

# Creates Blueprint
item_bp = Blueprint("item_bp",__name__)

from . import routes_create_item, routes_query_item