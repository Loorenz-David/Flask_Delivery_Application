from typing import Dict, Any
from sqlalchemy.orm import Query

from Delivery_app_BK.models import db, Vehicle
from Delivery_app_BK.services.utils import inject_team_id, model_requires_team

from ....context import ServiceContext
from ...utils import apply_pagination_by_id


def find_vehicles(
    params: Dict[str, Any],
    ctx: ServiceContext,
    query: Query | None = None,
):
    query = query or db.session.query(Vehicle)

    if model_requires_team(Vehicle) and ctx.inject_team_id:
        params = inject_team_id(params, ctx)

    if "team_id" in params:
        query = query.filter(Vehicle.team_id == params.get("team_id"))

    if "client_id" in params:
        query = query.filter(Vehicle.client_id == params.get("client_id"))

    if "name" in params:
        name = params.get("name").strip()
        query = query.filter(Vehicle.name.ilike(f"{name}%"))

    if "travel_mode" in params:
        query = query.filter(Vehicle.travel_mode == params.get("travel_mode"))

    sort = params.get("sort", "id_desc")
    if sort == "id_asc":
        query = query.order_by(Vehicle.id.asc())
    else:
        query = query.order_by(Vehicle.id.desc())

    query = apply_pagination_by_id(
        query,
        id_column=Vehicle.id,
        params=params,
        sort=sort,
    )

    return query
