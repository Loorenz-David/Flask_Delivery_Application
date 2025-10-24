# Third-party dependencies
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

# Locat Imports
from Delivery_app_BK.debug_logger import logger
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models.managers import ObjectFiller
from Delivery_app_BK.services import (
    service_create_item_category,
    service_create_item_type,
    service_create_item_property,
    service_create_item,
    service_create_item_state,
    service_create_item_position,
)
from . import item_bp



# CREATE ItemCategory Instance
@item_bp.route("/create_item_category", methods=["POST"])
def create_item_category():
    response = Response()
    incoming_data = request.get_json()

    type_build = ObjectFiller.fill_object(
        data = incoming_data,
        fill_function = service_create_item_category,
        response = response,
        reference = "Item Category"
    )

    return response.build()

# CREATE ItemType Instance
@item_bp.route("/create_item_type", methods=["POST"])
def create_item_type():
    response = Response()
    incoming_data = request.get_json()

    type_build = ObjectFiller.fill_object(
        data = incoming_data,
        fill_function = service_create_item_type,
        response = response,
        reference = "Item Type"
    )
    

    return response.build()


# CREATE ItemProperty Instance
@item_bp.route("/create_item_property", methods=["POST"])
def create_item_property():
    response = Response()
    incoming_data = request.get_json()

    properties_build = ObjectFiller.fill_object(
        data = incoming_data,
        fill_function = service_create_item_property,
        response = response,
        reference = "Item Property"
    )
    
    return response.build()

# CREATE Item Instance
@item_bp.route("/create_item",methods=['POST'])
def create_item ():
    response = Response()
    incoming_data = request.get_json()

    item_build = ObjectFiller.fill_object(
        data = incoming_data,
        fill_function = service_create_item,
        response = response,
        reference = "Item"
    )

    return response.build()


# CREATE ItemState Instance
@item_bp.route("/create_item_state", methods=["POST"])
def create_item_state():
    response = Response()
    incoming_data = request.get_json()

    ObjectFiller.fill_object(
        data=incoming_data,
        fill_function=service_create_item_state,
        response=response,
        reference="Item State",
    )

    return response.build()


# CREATE ItemPosition Instance
@item_bp.route("/create_item_position", methods=["POST"])
def create_item_position():
    response = Response()
    incoming_data = request.get_json()

    ObjectFiller.fill_object(
        data=incoming_data,
        fill_function=service_create_item_position,
        response=response,
        reference="Item Position",
    )

    return response.build()
