from __future__ import annotations

from typing import Any

from sqlalchemy import String, or_
from sqlalchemy.orm import Query

from Delivery_app_BK.models import Costumer, CostumerAddress, CostumerPhone, db
from Delivery_app_BK.services.utils import inject_team_id, model_requires_team

from ...context import ServiceContext
from ..utils import apply_pagination_by_date


def find_costumers(
    params: dict[str, Any],
    ctx: ServiceContext,
    query: Query | None = None,
):
    query = query or db.session.query(Costumer)

    params_dict = dict(params or {})
    if model_requires_team(Costumer) and ctx.inject_team_id:
        params_dict = inject_team_id(params_dict, ctx)

    if "team_id" in params_dict:
        query = query.filter(Costumer.team_id == params_dict.get("team_id"))

    q = str(params_dict.get("q") or "").strip()
    if q:
        pattern = f"%{q}%"
        query = query.outerjoin(CostumerAddress, CostumerAddress.costumer_id == Costumer.id)
        query = query.outerjoin(CostumerPhone, CostumerPhone.costumer_id == Costumer.id)
        query = query.filter(
            or_(
                Costumer.first_name.ilike(pattern),
                Costumer.last_name.ilike(pattern),
                Costumer.email.ilike(pattern),
                CostumerPhone.phone.cast(String).ilike(pattern),
                CostumerAddress.address.cast(String).ilike(pattern),
            )
        )
        query = query.distinct(Costumer.id)

    sort = str(params_dict.get("sort") or "").lower().strip()
    if sort == "last_name_asc":
        query = query.order_by(
            Costumer.last_name.asc(),
            Costumer.id.asc(),
        )
        return query
    else:
        query = query.order_by(
            Costumer.created_at.desc(),
            Costumer.id.desc(),
        )

    query = apply_pagination_by_date(
        query=query,
        date_column=Costumer.created_at,
        id_column=Costumer.id,
        params=params_dict,
        sort="date_asc" if sort == "created_at_asc" else "date_desc",
    )

    return query
