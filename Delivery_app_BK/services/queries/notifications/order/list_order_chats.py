from Delivery_app_BK.models import db, OrderChat

from ....context import ServiceContext
from .find_order_chats import find_order_chats
from .order_chats_stats import order_chats_stats
from .serialize_order_chats import serialize_order_chats
from ...utils import build_pagination


def list_order_chats(ctx: ServiceContext, order_id: int | None = None):
    base_query = db.session.query(OrderChat)
    if order_id is not None:
        base_query = base_query.filter(OrderChat.order_id == order_id)

    query = find_order_chats(
        params=ctx.query_params,
        ctx=ctx,
        query=base_query,
    )

    limit = int(ctx.query_params.get("limit", 50))
    results = query.limit(limit + 1).all()
    has_more = len(results) > limit
    page_instances = results[:limit]

    pagination = build_pagination(
        page_instances=page_instances,
        has_more=has_more,
        date_attr="creation_date",
        id_attr="id",
        ctx=ctx,
    )

    serialized = serialize_order_chats(
        instances=page_instances,
        ctx=ctx,
    )

    stats = order_chats_stats(
        query=query,
        ctx=ctx,
    )

    return {
        "order_chats": serialized,
        "order_chats_pagination": pagination,
        "order_chats_stats": stats,
    }
