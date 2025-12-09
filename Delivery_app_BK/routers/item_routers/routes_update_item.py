# Third-party dependencies
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.services import (
    service_update_item,
    service_update_item_category,
    service_update_item_type,
    service_update_item_property,
    service_update_item_state,
    service_update_item_position,
)
from . import item_bp
from Delivery_app_BK.routers.utils.response import Response

# CREATE Item Instance
@item_bp.route("/update_item",methods=['PUT'])
@jwt_required()
def update_item ():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        response=response,
        fill_function=service_update_item,
        reference="Item",
        add_to_session=False,
        action_type='update',
    )
    
    return response.build()


@item_bp.route("/update_item_category", methods=['PUT'])
@jwt_required()
def update_item_category():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        response=response,
        fill_function=service_update_item_category,
        reference="Item Category",
        add_to_session=False,
        action_type='update',
    )

    return response.build()


@item_bp.route("/update_item_type", methods=['PUT'])
@jwt_required()
def update_item_type():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        response=response,
        fill_function=service_update_item_type,
        reference="Item Type",
        add_to_session=False,
        action_type='update',
    )

    return response.build()


@item_bp.route("/update_item_property", methods=['PUT'])
@jwt_required()
def update_item_property():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        response=response,
        fill_function=service_update_item_property,
        reference="Item Property",
        add_to_session=False,
        action_type='update',
    )

    return response.build()


@item_bp.route("/update_item_state", methods=['PUT'])
@jwt_required()
def update_item_state():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        response=response,
        fill_function=service_update_item_state,
        reference="Item State",
        add_to_session=False,
        action_type='update',
    )

    return response.build()


@item_bp.route("/update_item_position", methods=['PUT'])
@jwt_required()
def update_item_position():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        response=response,
        fill_function=service_update_item_position,
        reference="Item Position",
        add_to_session=False,
        action_type='update',
    )

    return response.build()
