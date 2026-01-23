from ....context import ServiceContext
from ...utils import build_id_pagination
from .find_warehouses import find_warehouses
from .serialize_warehouses import serialize_warehouses


def list_warehouses(ctx: ServiceContext):
    query = find_warehouses(ctx.query_params, ctx)

    limit = int(ctx.query_params.get("limit", 50))
    results = query.limit(limit + 1).all()
    has_more = len(results) > limit
    page_instances = results[:limit]

    pagination = build_id_pagination(
        page_instances=page_instances,
        has_more=has_more,
        ctx=ctx,
    )

    serialized = serialize_warehouses(
        instances=page_instances,
        ctx=ctx,
    )

    return {
        "warehouses": serialized,
        "warehouses_pagination": pagination,
    }
