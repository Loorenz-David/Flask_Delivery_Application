from sqlalchemy import func, distinct
from sqlalchemy.orm import Query
from Delivery_app_BK.models import Order, Item, db
from ...context import ServiceContext


def order_stats(query: Query, ctx: ServiceContext):
    # Remove ordering & pagination
    base_query = query.order_by(None).limit(None).offset(None)

    # Convert to subquery of order ids only
    order_subquery = base_query.with_entities(Order.id).subquery()

    # --- Order counts ---
    total_orders = (
        db.session.query(func.count())
        .select_from(order_subquery)
        .scalar()
    )

    state_count = (
        db.session.query(
            Order.order_state_id,
            func.count(distinct(Order.id))
        )
        .join(order_subquery, Order.id == order_subquery.c.id)
        .group_by(Order.order_state_id)
        .all()
    )

    # --- Item count (no duplicate join issue anymore) ---
    item_count = (
        db.session.query(func.count(Item.id))
        .join(order_subquery, Item.order_id == order_subquery.c.id)
        .scalar()
    )

    return {
        "orders": {
            "total": total_orders,
            "by_state": {
                state_id: count
                for state_id, count in state_count
                if state_id is not None
            },
        },
        "items": {
            "total": item_count
        },
    }