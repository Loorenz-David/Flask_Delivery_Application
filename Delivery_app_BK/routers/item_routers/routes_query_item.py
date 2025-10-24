# Third-party dependencies
from flask import request

# Locat Imports

from Delivery_app_BK.models import Item
from Delivery_app_BK.models.managers.object_searcher import FindObjects
from . import item_bp
from Delivery_app_BK.routers.utils.response import Response

@item_bp.route("/query_item",methods=['POST'])
def query_item ():
    
    response = Response()
    incoming_data = request.get_json()

    FindObjects.find_objects(
        response=response,
        Model=Item,
        incoming_data=incoming_data,
    )
    
    return response.build()
