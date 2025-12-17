# Third-party dependencies
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from Delivery_app_BK.routers.utils.role_decorator import role_required


# Locat Imports
from . import order_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models import Order
from Delivery_app_BK.models.managers.object_searcher import FindObjects
from .orders_default_data_request import ORDER_REQUESTED_DATA

@order_bp.route("/query_order",methods=['POST'])
@jwt_required()
@role_required([1, 2])
def query_order ():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)
    request_payload = response.incoming_data or {}
    if not isinstance(request_payload, dict):
        request_payload = {}
    if not request_payload.get('requested_data'):
        request_payload['requested_data'] = ORDER_REQUESTED_DATA
        response.incoming_data = request_payload

    FindObjects.find_objects(
        response=response,
        Model=Order,
        identity=identity,
    )
    return response.build()
