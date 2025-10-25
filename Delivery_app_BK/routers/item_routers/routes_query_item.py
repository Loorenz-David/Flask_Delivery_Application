# Third-party dependencies
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

# Locat Imports

from Delivery_app_BK.models import Item
from Delivery_app_BK.models.managers.object_searcher import FindObjects
from . import item_bp
from Delivery_app_BK.routers.utils.response import Response

@item_bp.route("/query_item",methods=['POST'])
@jwt_required()
def query_item ():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    FindObjects.find_objects(
        response=response,
        Model=Item,
        identity=identity,
    )
    
    return response.build()
