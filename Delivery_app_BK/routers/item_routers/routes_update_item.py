# Third-party dependencies
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.services import service_update_item
from . import item_bp
from Delivery_app_BK.routers.utils.response import Response

# CREATE Item Instance
@item_bp.route("/update_item",methods=['PUT'])
@jwt_required()
def update_item ():
    identity = get_jwt_identity()
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
