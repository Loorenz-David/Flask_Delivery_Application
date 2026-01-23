from Delivery_app_BK.models import DeliveryPlan

from ..utils import build_pagination
from ...context import ServiceContext
from .find_plans import find_plans
from .serialize_plan import serialize_plans
from .plan_stats import plan_stats



def list_delivery_plans(ctx: ServiceContext):
    query = find_plans( ctx.query_params, ctx )

    limit = int(ctx.query_params.get("limit", 50))
    results = query.limit(limit + 1).all()
    has_more = len(results) > limit

    page_instances = results[ :limit ]

    pagination = build_pagination( 
        page_instances = page_instances, 
        has_more = has_more, 
        date_attr = 'start_date',
        id_attr = 'id',
        ctx = ctx 
    )
    

    serialize_objects = serialize_plans( 
        instances = page_instances,
        ctx = ctx
    )

    stats = plan_stats( 
        query = query, 
        ctx = ctx
    )


    return {
        "delivery_plan": serialize_objects,
        "delivery_plan_stats": stats,
        "delivery_plan_pagination": pagination
    }

