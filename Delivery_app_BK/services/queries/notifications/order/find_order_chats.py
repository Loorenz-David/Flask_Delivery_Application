from typing import Dict, Any
from sqlalchemy.orm import Query

from Delivery_app_BK.models import db, OrderChat
from Delivery_app_BK.services.utils import inject_team_id, model_requires_team

from ....context import ServiceContext
from ...utils import apply_pagination_by_date
from ....utils import to_datetime


def find_order_chats(
    params: Dict[str, Any],
    ctx: ServiceContext,
    query: Query | None = None,
):
    query = query or db.session.query(OrderChat)

    if model_requires_team( OrderChat ) and ctx.inject_team_id:
        params = inject_team_id( params, ctx )
    
    if "team_id" in params:
        query = query.filter( OrderChat.team_id == params.get( "team_id" ) )


    if "order_id" in params:
        order_ids = params.get("order_id")
        if not isinstance(order_ids, (list, tuple)):
            order_ids = [order_ids]
        query = query.filter(OrderChat.order_id.in_(order_ids))

    if "user_id" in params:
        user_ids = params.get("user_id")
        if not isinstance(user_ids, (list, tuple)):
            user_ids = [user_ids]
        query = query.filter(OrderChat.user_id.in_(user_ids))

    if "creation_date_from" in params:
        creation_date_from = to_datetime(params.get("creation_date_from"))
        query = query.filter(OrderChat.creation_date >= creation_date_from)

    if "creation_date_to" in params:
        creation_date_to = to_datetime(params.get("creation_date_to"))
        query = query.filter(OrderChat.creation_date <= creation_date_to)

    if params.get("sort") == "date_asc":
        query = query.order_by(OrderChat.creation_date.asc(), OrderChat.id.asc())
    else:
        query = query.order_by(OrderChat.creation_date.desc(), OrderChat.id.desc())

    query = apply_pagination_by_date(
        query=query,
        date_column=OrderChat.creation_date,
        id_column=OrderChat.id,
        params=params,
        sort=params.get("sort", "date_desc"),
    )

    return query
