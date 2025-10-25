from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.services import service_create_route
from . import route_bp



@route_bp.route("/create_route", methods=["POST"])
@jwt_required()
def create_route():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_create_route,
        response=response,
        reference="Route",
    )
    
    return response.build()
