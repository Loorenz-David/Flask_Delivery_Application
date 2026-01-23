
from Delivery_app_BK.models import db, Order
from Delivery_app_BK.errors import ValidationFailed, NotFound


from ...context import ServiceContext
from ..get_instance import get_instance 
from .serialize_order import serialize_orders


def get_order( order_id: int, ctx:ServiceContext ):

    found_order = get_instance(
        ctx = ctx,
        model = Order,
        value = order_id
    )

    if not found_order:
        raise NotFound(f"Order with id: {order_id} does not exist.")    
    
    serialize_object = serialize_orders(
        instances = [ found_order ],
        ctx = ctx
    )

    return {
        "order": serialize_object[0] if isinstance( serialize_object, list ) else serialize_object
    }
