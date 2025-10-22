# Third-party dependencies
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import traceback

# Locat Imports
from Delivery_app_BK.debug_logger import logger
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models import Item, db
from Delivery_app_BK.models.tables.items_models import ItemType, ItemCategory, ItemProperty
from Delivery_app_BK.models.schemas.items_schema import ItemCreation,ItemTypeCreation, ItemCategoryCreation, ItemPropertyCreation
from Delivery_app_BK.models.managers.object_creator import ObjectCreator
from Delivery_app_BK.services import service_create_item_category, service_create_item_type, service_create_item_property, service_create_item
from . import item_bp



# CREATE ItemCategory Instance
@item_bp.route("/create_item_category", methods=["POST"])
def create_item_category():
    response = Response()
    incoming_data = request.get_json()

    type_build = ObjectCreator.create(
        Obj = ItemCategory,
        data = incoming_data,
        creation_function = service_create_item_category,
        response = response,
        reference = "Item Category"
    )

    return response.build()

# CREATE ItemType Instance
@item_bp.route("/create_item_type", methods=["POST"])
def create_item_type():
    response = Response()
    incoming_data = request.get_json()

    type_build = ObjectCreator.create(
        Obj = ItemType,
        data = incoming_data,
        creation_function = service_create_item_type,
        response = response,
        reference = "Item Type"
    )
    

    return response.build()


# CREATE ItemProperty Instance
@item_bp.route("/create_item_property", methods=["POST"])
def create_item_property():
    response = Response()
    incoming_data = request.get_json()

    properties_build = ObjectCreator.create(
        Obj = ItemProperty,
        data = incoming_data,
        creation_function = service_create_item_property,
        response = response,
        reference = "Item Property"
    )
    
    return response.build()

# CREATE Item Instance
@item_bp.route("/create_item",methods=['POST'])
def create_item ():
    response = Response()
    incoming_data = request.get_json()

    item_build = ObjectCreator.create(
        Obj = Item,
        data = incoming_data,
        creation_function = service_create_item,
        response = response,
        reference = "Item"
    )

    return response.build()
