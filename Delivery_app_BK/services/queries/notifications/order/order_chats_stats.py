from sqlalchemy import func
from sqlalchemy.orm import Query

from Delivery_app_BK.models import OrderChat

from ....context import ServiceContext


def order_chats_stats(query: Query, ctx: ServiceContext):
    query = query.order_by(None).limit(None).offset(None)

    total_chats = query.with_entities(
        func.count(OrderChat.id)
    ).scalar()

    return {
        "order_chats": {
            "total": total_chats
        }
    }
