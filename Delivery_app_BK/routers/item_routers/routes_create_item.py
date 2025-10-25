# Third-party dependencies
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

# Locat Imports
from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.services import (
    service_create_item_category,
    service_create_item_type,
    service_create_item_property,
    service_create_item,
    service_create_item_state,
    service_create_item_position,
)
from . import item_bp
from Delivery_app_BK.routers.utils.response import Response


# CREATE ItemCategory Instance
@item_bp.route("/create_item_category", methods=["POST"])
@jwt_required()
def create_item_category():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        response=response,
        fill_function=service_create_item_category,
        reference="Item Category",
    )
    return response.build()

# CREATE ItemType Instance
@item_bp.route("/create_item_type", methods=["POST"])
@jwt_required()
def create_item_type():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        response=response,
        fill_function=service_create_item_type,
        reference="Item Type",
    )
    return response.build()


# CREATE ItemProperty Instance
@item_bp.route("/create_item_property", methods=["POST"])
@jwt_required()
def create_item_property():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        response=response,
        fill_function=service_create_item_property,
        reference="Item Property",
    )
    
    return response.build()

# CREATE Item Instance
@item_bp.route("/create_item",methods=['POST'])
@jwt_required()
def create_item ():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        response=response,
        fill_function=service_create_item,
        reference="Item",
    )

    return response.build()


# CREATE ItemState Instance
@item_bp.route("/create_item_state", methods=["POST"])
@jwt_required()
def create_item_state():
    print('in create item state')
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)
    print(response.incoming_data)
    ObjectFiller.fill_object(
        fill_function=service_create_item_state,
        response=response,
        reference="Item State",
    )

    return response.build()


# CREATE ItemPosition Instance
@item_bp.route("/create_item_position", methods=["POST"])
@jwt_required()
def create_item_position():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_create_item_position,
        response=response,
        reference="Item Position",
    )

    return response.build()
