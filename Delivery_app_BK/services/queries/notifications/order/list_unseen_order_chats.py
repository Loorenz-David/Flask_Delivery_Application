
from Delivery_app_BK.models import db, OrderChat, NotificationRead
from Delivery_app_BK.errors import ValidationFailed

from ....context import ServiceContext
from .find_order_chats import find_order_chats
from .order_chats_stats import order_chats_stats
from .serialize_order_chats import serialize_order_chats
from ...utils import build_pagination


def list_unseen_order_chats(ctx: ServiceContext):
    if not ctx.user_id:
        raise ValidationFailed("User id is required to fetch unseen chats.")

    base_query = db.session.query(OrderChat).filter(
        OrderChat.user_id != ctx.user_id,
        ~OrderChat.notification_reads.any(NotificationRead.user_id == ctx.user_id)
    )

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
