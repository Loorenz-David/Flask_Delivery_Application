from flask import request

from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.services import service_create_route
from . import route_bp



@route_bp.route("/create_route", methods=["POST"])
def create_route():
    response = Response()
    incoming_data = request.get_json()

    ObjectFiller.fill_object(
        data=incoming_data,
        fill_function=service_create_route,
        response=response,
        reference="Route",
    )
    
    return response.build()
