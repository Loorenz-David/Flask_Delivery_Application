from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from Delivery_app_BK.routers.utils.role_decorator import role_required


from . import route_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.services.routes_services.service_optimize import (
    service_optimize_route,
    service_change_optimization_indx,
)


@route_bp.route("/optimize_route", methods=["POST"])
@jwt_required()
@role_required([1, 2, 3])
def optimize_route():

    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)
    
    if not response.error:
        service_optimize_route(response=response, identity=identity)

    return response.build()


@route_bp.route("/change_optimization_indx", methods=["POST"])
@jwt_required()
@role_required([1, 2, 3])
def change_optimization_indx():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    if not response.error:
        service_change_optimization_indx(response=response, identity=identity)

    return response.build()
