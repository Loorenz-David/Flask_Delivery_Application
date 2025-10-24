# Third-party dependencies
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

# Locat Imports
from Delivery_app_BK.debug_logger import logger

from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.services import service_update_item
from . import item_bp
from Delivery_app_BK.routers.utils.response import Response

# CREATE Item Instance
@item_bp.route("/update_item",methods=['PUT'])
def update_item ():
    response = Response()
    incoming_data = request.get_json()

    item_update = ObjectFiller.fill_object(
        data = incoming_data,
        fill_function = service_update_item,
        response = response,
        reference = "Item",
        add_to_session = False,
        action_type = 'update'
    )
    
    return response.build()
