from Delivery_app_BK.models import db, OrderChat
from Delivery_app_BK.errors import NotFound

from ....context import ServiceContext
from ...get_instance import get_instance 
from .serialize_order_chats import serialize_order_chats


def get_order_chat(order_chat_id: int, ctx: ServiceContext):
    found_chat = get_instance(
        ctx = ctx,
        model = OrderChat,
        value = order_chat_id
    )

    if not found_chat:
        raise NotFound(f"Order chat with id: {order_chat_id} does not exist.")

    serialized = serialize_order_chats(
        instances=[found_chat],
        ctx=ctx,
    )

    return {
        "order_chat": serialized[0] if isinstance(serialized, list) else serialized
    }
