from Delivery_app_BK.models import DeliveryPlan

from ..utils import build_opaque_pagination
from ...context import ServiceContext
from .find_plans import find_plans
from .serialize_plan import serialize_plans
from .plan_stats import plan_stats



def list_delivery_plans(ctx: ServiceContext):
    query = find_plans( ctx.query_params, ctx )
    stats_query_params = {
        key: value
        for key, value in dict(ctx.query_params).items()
        if key not in {"after_cursor", "before_cursor", "limit"}
    }
    stats_query = find_plans(stats_query_params, ctx)

    limit = min(int(ctx.query_params.get("limit", MAX_PLAN_LIMIT)), MAX_PLAN_LIMIT)
    results = query.limit(limit + 1).all()
    has_more = len(results) > limit

    page_instances = results[ :limit ]

    pagination = build_opaque_pagination(
        page_instances = page_instances, 
        has_more = has_more, 
        date_attr = 'created_at',
        id_attr = 'id',
    )
    

    serialize_objects = serialize_plans( 
        instances = page_instances,
        ctx = ctx
    )

    stats = plan_stats( 
        query = stats_query, 
        ctx = ctx
    )


    return {
        "delivery_plan": serialize_objects,
        "delivery_plan_stats": stats,
        "delivery_plan_pagination": pagination
    }
MAX_PLAN_LIMIT = 25
