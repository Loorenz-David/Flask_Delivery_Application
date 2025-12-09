# Third-party dependencies
from flask import request
from flask_jwt_extended import jwt_required, get_jwt

# Local Imports
from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.services import (
    service_delete_item_category,
    service_delete_item_type,
    service_delete_item_property,
    service_delete_item,
    service_delete_item_state,
    service_delete_item_position,
)
from . import item_bp


@item_bp.route("/delete_item_category", methods=["DELETE"])
@jwt_required()
def delete_item_category():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        response=response,
        fill_function=service_delete_item_category,
        reference="Item Category",
        add_to_session=False,
        action_type='delete',
    )
    return response.build()


@item_bp.route("/delete_item_type", methods=["DELETE"])
@jwt_required()
def delete_item_type():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        response=response,
        fill_function=service_delete_item_type,
        reference="Item Type",
        add_to_session=False,
        action_type='delete',
    )
    return response.build()


@item_bp.route("/delete_item_property", methods=["DELETE"])
@jwt_required()
def delete_item_property():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        response=response,
        fill_function=service_delete_item_property,
        reference="Item Property",
        add_to_session=False,
        action_type='delete',
    )
    return response.build()


@item_bp.route("/delete_item", methods=["DELETE"])
@jwt_required()
def delete_item():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        response=response,
        fill_function=service_delete_item,
        reference="Item",
        add_to_session=False,
        action_type='delete',
    )
    return response.build()


@item_bp.route("/delete_item_state", methods=["DELETE"])
@jwt_required()
def delete_item_state():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_delete_item_state,
        response=response,
        reference="Item State",
        add_to_session=False,
        action_type='delete',
    )

    return response.build()


@item_bp.route("/delete_item_position", methods=["DELETE"])
@jwt_required()
def delete_item_position():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_delete_item_position,
        response=response,
        reference="Item Position",
        add_to_session=False,
        action_type='delete',
    )

    return response.build()
