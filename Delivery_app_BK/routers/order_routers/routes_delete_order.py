from flask import request
from flask_jwt_extended import jwt_required, get_jwt
from Delivery_app_BK.routers.utils.role_decorator import role_required

from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.services import service_delete_order
from . import order_bp


@order_bp.route('/delete_order', methods=['DELETE'])
@jwt_required()
@role_required([1])
def delete_order():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_delete_order,
        response=response,
        reference='Order',
        add_to_session=False,
        action_type='delete',
    )

    return response.build()
