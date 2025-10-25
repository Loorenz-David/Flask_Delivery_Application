from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.services import service_create_order
from . import order_bp


@order_bp.route("/create_order", methods=["POST"])
@jwt_required()
def create_order():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_create_order,
        response=response,
        reference="Order",
    )

    return response.build()
