from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
import asyncio

from . import notifications_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models.managers.object_notificator import ObjectNotificator

@notifications_bp.route("/send_notification", methods=["POST"])
@jwt_required()
def send_notification():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    if response.error:
        return response.build()
    
    # organizices the incoming request data
    notification = ObjectNotificator(
        response = response,
        identity = identity
    )
    

    # sends messages to the specify channels on the request data, 
    # add succesfull and fail messages to the response payload
    notification.send_message_sync()

    return response.build()