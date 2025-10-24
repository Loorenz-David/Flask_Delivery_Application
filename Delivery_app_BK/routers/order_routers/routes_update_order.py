from flask import request

from Delivery_app_BK.models.managers import ObjectFiller
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.services import service_update_order
from . import order_bp


@order_bp.route("/update_order", methods=["PUT"])
def update_order():
    response = Response()
    incoming_data = request.get_json()

    ObjectFiller.fill_object(
        data=incoming_data,
        fill_function=service_update_order,
        response=response,
        reference="Order",
        add_to_session=False,
        action_type="update",
    )

    return response.build()
