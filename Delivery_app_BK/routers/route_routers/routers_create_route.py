from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt


from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.services import service_create_route
from . import route_bp



@route_bp.route("/create_route", methods=["POST"])
@jwt_required()
def create_route():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    created_routes = ObjectFiller.fill_object(
        fill_function=service_create_route,
        response=response,
        reference="Route",
    )

    response.set_created_payload(created_routes)
    
    return response.build()
