from Delivery_app_BK.models import db, Order

from ..utils import build_pagination
from ...context import ServiceContext
from .find_orders import find_orders
from .serialize_order import serialize_orders
from .order_stats import order_stats



def list_orders(ctx: ServiceContext, plan_id: int | None = None):
    base_query = db.session.query(Order)
    if plan_id is not None:
        base_query = base_query.filter(Order.delivery_plan_id == plan_id)

    query = find_orders(ctx.query_params, ctx, query=base_query)

    limit = int(ctx.query_params.get("limit", 50))
    results = query.limit(limit + 1).all()
    has_more = len(results) > limit

    page_instances = results[ :limit ]

    pagination = build_pagination( 
        page_instances = page_instances, 
        has_more = has_more, 
        date_attr = 'earliest_delivery_date',
        id_attr = 'id',
        ctx = ctx 
    )
    

    serialize_objects = serialize_orders( 
        instances = page_instances,
        ctx = ctx
    )

    stats = order_stats( 
        query = query, 
        ctx = ctx
    )


    return {
        "order": serialize_objects,
        "order_stats": stats,
        "order_pagination": pagination
    }
