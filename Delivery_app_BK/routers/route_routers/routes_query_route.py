# Third-party dependencies
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

# Locat Imports
from . import route_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models import Route
from .routes_default_data_request import ROUTE_REQUESTED_DATA
from Delivery_app_BK.services.routes_services.service_query_routes import service_query_routes

@route_bp.route("/query_route",methods=['POST'])
@jwt_required()
def query_route ():
    
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)
    request_payload = response.incoming_data or {}
    if not isinstance(request_payload, dict):
        request_payload = {}
    if not request_payload.get('requested_data'):
        request_payload['requested_data'] = ROUTE_REQUESTED_DATA
        response.incoming_data = request_payload

    payload = service_query_routes(
        request_payload=request_payload,
        identity=identity,
    )
    response.set_payload(payload)
    # response.compress_payload()
    return response.build()
