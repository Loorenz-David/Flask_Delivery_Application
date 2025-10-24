from flask import request

from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.services import service_create_order
from . import order_bp


@order_bp.route("/create_order", methods=["POST"])
def create_order():
    response = Response()
    incoming_data = request.get_json()

    ObjectFiller.fill_object(
        data=incoming_data,
        fill_function=service_create_order,
        response=response,
        reference="Order",
    )

    return response.build()
