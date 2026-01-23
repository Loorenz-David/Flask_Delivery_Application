from typing import Type
from sqlalchemy import func, distinct
from sqlalchemy.orm import Query

from Delivery_app_BK.models import  Order, Item

from ...context import ServiceContext


def order_stats( query:Query, ctx:ServiceContext ):
    query = query.order_by(None).limit(None).offset(None) 
    
    total_orders = query.with_entities(
        func.count( Order.id )
    ).scalar()

    state_count = (
        query
        .with_entities(
            Order.order_state_id,
            func.count( distinct( Order.id ) )
        )
        .group_by( Order.order_state_id )
        .all()
    )

    item_count = (
        query
        .join( Item, Item.order_id == Order.id )
        .with_entities( distinct( func.count( Item.id ) ) )
        .scalar()
    )

    return {
        "orders": {
            "total": total_orders,
            "by_state": {
                state_id: count for state_id, count in state_count
            }
        },
        "items":{
            "total": item_count
        }
    }