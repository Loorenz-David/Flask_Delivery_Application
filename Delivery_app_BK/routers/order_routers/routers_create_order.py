from flask import request
from flask_jwt_extended import jwt_required, get_jwt
from Delivery_app_BK.routers.utils.role_decorator import role_required


from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.models.managers.object_notificator import ObjectNotificator
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.services import service_create_order
from . import order_bp


@order_bp.route("/create_order", methods=["POST"])
@jwt_required()
@role_required([1])
def create_order():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    if response.error:
        return response.build()

    message_template = None
    if isinstance(response.incoming_data, dict):
        message_template = response.incoming_data.pop("message_template", None)

    created_orders = ObjectFiller.fill_object(
        fill_function=service_create_order,
        response=response,
        reference="Order",
    )
    response.set_created_payload(created_orders)

    message_status = None
    if message_template:
        try:
            client_payload = response.incoming_data or {}
            try:
                client_payload = dict(client_payload)
            except Exception:
                pass
            try:
                if created_orders and hasattr(created_orders[0], "id"):
                    client_payload["id"] = getattr(created_orders[0], "id")
            except Exception:
                pass
            message_request = {
                "data": {
                    "templates_id": message_template,
                    "target_clients": [client_payload],
                },
                "is_compress": False,
            }
            notification_response = Response(incoming_data=message_request, identity=identity)
            notification = ObjectNotificator(
                response=notification_response,
                identity=identity,
            )
            notification.send_message_sync()
            if notification_response.error:
                message_status = {"error": notification_response.error}
            else:
                message_status = notification_response.payload
        except Exception as e:
            message_status = {"error": str(e)}

    if isinstance(response.payload, dict) and message_status is not None:
        response.payload["message_status"] = message_status

    return response.build()
