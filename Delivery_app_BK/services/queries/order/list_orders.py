from Delivery_app_BK.models import db, Order
from sqlalchemy.orm import selectinload

from ..utils import build_opaque_pagination
from ...context import ServiceContext
from .find_orders import find_orders
from .serialize_order import serialize_orders
from .order_stats import order_stats

MAX_ORDER_LIMIT = 200


def list_orders(ctx: ServiceContext, plan_id: int | None = None):
    base_query = db.session.query(Order).options(
        selectinload(Order.delivery_windows),
        selectinload(Order.items),
    )
    if plan_id is not None:
        base_query = base_query.filter(Order.delivery_plan_id == plan_id)

    query = find_orders(ctx.query_params, ctx, query=base_query)
    stats_query_params = {
        key: value
        for key, value in dict(ctx.query_params).items()
        if key not in {"after_cursor", "before_cursor", "limit"}
    }
    stats_query = find_orders(stats_query_params, ctx, query=base_query)

    limit = min(int(ctx.query_params.get("limit", MAX_ORDER_LIMIT)), MAX_ORDER_LIMIT)
    results = query.limit(limit + 1).all()
    has_more = len(results) > limit

    page_instances = results[ :limit ]

    pagination = build_opaque_pagination(
        page_instances = page_instances, 
        has_more = has_more, 
        date_attr = 'creation_date',
        id_attr = 'id',
    )
    

    serialize_objects = serialize_orders( 
        instances = page_instances,
        ctx = ctx
    )

    stats = order_stats( 
        query = stats_query, 
        ctx = ctx
    )

    return {
        "order": serialize_objects,
        "order_stats": stats,
        "order_pagination": pagination
    }
