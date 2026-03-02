from __future__ import annotations

from sqlalchemy.orm import selectinload

from Delivery_app_BK.models import Costumer, db

from ...context import ServiceContext
from ..utils import build_pagination
from .costumer_stats import costumer_stats
from .find_costumers import find_costumers
from .serialize_costumer import serialize_costumers


def list_costumers(ctx: ServiceContext):
    base_query = db.session.query(Costumer).options(
        selectinload(Costumer.addresses),
        selectinload(Costumer.phones),
        selectinload(Costumer.operating_hours),
    )

    query = find_costumers(ctx.query_params, ctx, query=base_query)
    limit = int(ctx.query_params.get("limit", 50))
    results = query.limit(limit + 1).all()
    has_more = len(results) > limit
    page_instances = results[:limit]

    pagination = build_pagination(
        page_instances=page_instances,
        has_more=has_more,
        date_attr="created_at",
        id_attr="id",
        ctx=ctx,
    )

    return {
        "costumer": serialize_costumers(page_instances),
        "costumer_stats": costumer_stats(ctx, base_query=query),
        "costumer_pagination": pagination,
    }

