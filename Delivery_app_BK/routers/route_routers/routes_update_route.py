from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.services import service_update_route
from . import route_bp


@route_bp.route("/update_route", methods=["PUT"])
@jwt_required()
def update_route():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_update_route,
        response=response,
        reference="Route",
        add_to_session=False,
        action_type="update",
    )

    return response.build()
