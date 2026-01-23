from ....context import ServiceContext
from ...utils import build_id_pagination
from .find_label_templates import find_label_templates
from .serialize_label_templates import serialize_label_templates


def list_label_templates(ctx: ServiceContext):
    query = find_label_templates(ctx.query_params, ctx)

    limit = int(ctx.query_params.get("limit", 50))
    results = query.limit(limit + 1).all()
    has_more = len(results) > limit
    page_instances = results[:limit]

    pagination = build_id_pagination(
        page_instances=page_instances,
        has_more=has_more,
        ctx=ctx,
    )

    serialized = serialize_label_templates(
        instances=page_instances,
        ctx=ctx,
    )

    return {
        "label_templates": serialized,
        "label_templates_pagination": pagination,
    }
