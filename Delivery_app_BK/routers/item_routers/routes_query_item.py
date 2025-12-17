# Third-party dependencies
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from Delivery_app_BK.routers.utils.role_decorator import role_required


# Locat Imports

from Delivery_app_BK.models import Item, ItemType, ItemCategory, ItemProperty, ItemState, ItemPosition
from Delivery_app_BK.models.managers.object_searcher import FindObjects
from . import item_bp
from Delivery_app_BK.routers.utils.response import Response
from .items_default_data_request import (
    ITEM_REQUESTED_DATA,
    ITEM_OPTIONS_REQUESTED_DATA,
    ITEM_TYPE_REQUESTED_DATA,
    ITEM_CATEGORY_REQUESTED_DATA,
    ITEM_PROPERTY_REQUESTED_DATA,
    ITEM_STATE_REQUESTED_DATA,
    ITEM_POSITION_REQUESTED_DATA,
)
from Delivery_app_BK.services.item_services.service_query_options import service_query_item_options

@item_bp.route("/query_item",methods=['POST'])
@jwt_required()
@role_required([1, 2])
def query_item ():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)
    request_payload = response.incoming_data or {}
    if not isinstance(request_payload, dict):
        request_payload = {}
    if not request_payload.get('requested_data'):
        request_payload['requested_data'] = ITEM_REQUESTED_DATA
        response.incoming_data = request_payload

    FindObjects.find_objects(
        response=response,
        Model=Item,
        identity=identity,
    )
    
    return response.build()

@item_bp.route("/query_item_options", methods=['POST'])
@jwt_required()
@role_required([1, 2])
def query_item_options():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)
    request_payload = response.incoming_data or {}
    if not isinstance(request_payload, dict):
        request_payload = {}
    if not request_payload.get('requested_data'):
        request_payload['requested_data'] = ITEM_OPTIONS_REQUESTED_DATA
        response.incoming_data = request_payload

    payload = service_query_item_options(request_payload=request_payload, identity=identity)
    response.set_payload(payload)
    return response.build()


@item_bp.route("/query_item_type", methods=['POST'])
@jwt_required()
@role_required([1, 2])
def query_item_type():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)
    request_payload = response.incoming_data or {}
    if not isinstance(request_payload, dict):
        request_payload = {}
    if not request_payload.get('requested_data'):
        request_payload['requested_data'] = ITEM_TYPE_REQUESTED_DATA
        response.incoming_data = request_payload

    FindObjects.find_objects(
        response=response,
        Model=ItemType,
        identity=identity,
    )

    return response.build()


@item_bp.route("/query_item_category", methods=['POST'])
@jwt_required()
@role_required([1, 2])
def query_item_category():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)
    request_payload = response.incoming_data or {}
    if not isinstance(request_payload, dict):
        request_payload = {}
    if not request_payload.get('requested_data'):
        request_payload['requested_data'] = ITEM_CATEGORY_REQUESTED_DATA
        response.incoming_data = request_payload

    FindObjects.find_objects(
        response=response,
        Model=ItemCategory,
        identity=identity,
    )

    return response.build()


@item_bp.route("/query_item_property", methods=['POST'])
@jwt_required()
@role_required([1, 2])
def query_item_property():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)
    request_payload = response.incoming_data or {}
    if not isinstance(request_payload, dict):
        request_payload = {}
    if not request_payload.get('requested_data'):
        request_payload['requested_data'] = ITEM_PROPERTY_REQUESTED_DATA
        response.incoming_data = request_payload

    FindObjects.find_objects(
        response=response,
        Model=ItemProperty,
        identity=identity,
    )

    return response.build()


@item_bp.route("/query_item_state", methods=['POST'])
@jwt_required()
@role_required([1, 2, 3])
def query_item_state():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)
    request_payload = response.incoming_data or {}
    if not isinstance(request_payload, dict):
        request_payload = {}
    if not request_payload.get('requested_data'):
        request_payload['requested_data'] = ITEM_STATE_REQUESTED_DATA
        response.incoming_data = request_payload

    FindObjects.find_objects(
        response=response,
        Model=ItemState,
        identity=identity,
    )

    return response.build()


@item_bp.route("/query_item_position", methods=['POST'])
@jwt_required()
@role_required([1, 2, 3])
def query_item_position():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)
    request_payload = response.incoming_data or {}
    if not isinstance(request_payload, dict):
        request_payload = {}
    if not request_payload.get('requested_data'):
        request_payload['requested_data'] = ITEM_POSITION_REQUESTED_DATA
        response.incoming_data = request_payload

    FindObjects.find_objects(
        response=response,
        Model=ItemPosition,
        identity=identity,
    )

    return response.build()
