# Third-party dependencies
from flask import request
from flask_jwt_extended import jwt_required, get_jwt
from Delivery_app_BK.routers.utils.role_decorator import role_required

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
from Delivery_app_BK.models import ItemType, ItemState, ItemProperty, ItemCategory, ItemPosition, db


@item_bp.route("/delete_item_category", methods=["DELETE"])
@jwt_required()
@role_required([1])
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
@role_required([1])
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
@role_required([1])
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
@role_required([1])
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
@role_required([1])
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
@role_required([1])
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


MODEL_MAP = {
    "ItemType": ItemType,
    "ItemState": ItemState,
    "ItemProperty": ItemProperty,
    "ItemCategory": ItemCategory,
    "ItemPosition": ItemPosition,
}


@item_bp.route("/delete_all_by_model", methods=["DELETE"])
@jwt_required()
@role_required([1])
def delete_all_by_model():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    try:
        payload = response.incoming_data or {}
        if not isinstance(payload, dict):
            raise ValueError("Payload must be an object with 'model' key.")
        model_key = payload.get("model")
        if model_key not in MODEL_MAP:
            raise ValueError("Invalid model name.")

        team_id = identity.get("team_id")
        if team_id is None:
            raise ValueError("Missing team_id in identity.")

        Model = MODEL_MAP[model_key]
        deleted = Model.query.filter_by(team_id=team_id).delete()
        db.session.commit()
        response.set_message(f"Deleted {deleted} records from {model_key}.")
        response.set_payload({"deleted": deleted})
    except Exception as error:
        db.session.rollback()
        response.set_error(str(error), status=400)
        response.set_message("Failed to delete records.")

    return response.build()
