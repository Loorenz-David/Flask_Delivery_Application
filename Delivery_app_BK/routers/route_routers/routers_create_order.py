from flask import request
from flask_jwt_extended import jwt_required, get_jwt

from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.services import service_create_order
from . import route_bp


@route_bp.route('/create_order', methods=['POST'])
@jwt_required()
def create_route_order():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    created_orders = ObjectFiller.fill_object(
        fill_function=service_create_order,
        response=response,
        reference='Order',
    )

    if created_orders:
        payload = []
        for order in created_orders:
            order_payload = {}
            if hasattr(order, 'id'):
                order_payload['id'] = order.id
            if hasattr(order, 'route_id'):
                order_payload['route_id'] = order.route_id
            delivery_items = getattr(order, 'delivery_items', None)
            if delivery_items:
                order_payload['delivery_items'] = [
                    {'id': getattr(item, 'id', None)}
                    for item in delivery_items
                    if hasattr(item, 'id')
                ]
            payload.append(order_payload)

        if payload:
            if len(payload) == 1:
                response.set_payload({'instance': payload[0]})
            else:
                response.set_payload({'items': payload})

    return response.build()
