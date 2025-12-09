from flask import request
from flask_jwt_extended import jwt_required, get_jwt

from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.services import service_update_order
from . import route_bp


@route_bp.route('/update_order', methods=['PUT'])
@jwt_required()
def update_route_order():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    updated_orders = ObjectFiller.fill_object(
        fill_function=service_update_order,
        response=response,
        reference='Order',
        add_to_session=False,
        action_type='update',
    )

    if updated_orders:
        created_payload = []
        for order in updated_orders:
            created_items = getattr(order, '_created_items_payload', None)
            if created_items:
                created_payload.extend(created_items)
        if created_payload:
            response.set_payload({'created_items': created_payload})

    return response.build()
