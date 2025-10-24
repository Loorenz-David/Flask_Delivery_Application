from flask import request

from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.services import service_update_route
from . import route_bp


@route_bp.route("/update_route", methods=["PUT"])
def update_route():
    response = Response()
    incoming_data = request.get_json()

    ObjectFiller.fill_object(
        data=incoming_data,
        fill_function=service_update_route,
        response=response,
        reference="Route",
        add_to_session=False,
        action_type="update",
    )

    return response.build()
