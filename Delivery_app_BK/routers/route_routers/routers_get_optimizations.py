from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from . import route_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.services.routes_services.service_optimize import (
    service_optimize_route,
)


@route_bp.route("/optimize_route", methods=["POST"])
@jwt_required()
def optimize_route():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    if not response.error:
        service_optimize_route(response=response, identity=identity)

    return response.build()
