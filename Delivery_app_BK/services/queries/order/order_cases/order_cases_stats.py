from sqlalchemy import func
from sqlalchemy.orm import Query

from Delivery_app_BK.models import OrderCase
from Delivery_app_BK.services.context import ServiceContext


def order_cases_stats(query: Query, ctx: ServiceContext):
    query = query.order_by(None).limit(None).offset(None)

    total_cases = query.with_entities(
        func.count(OrderCase.id)
    ).scalar()

    return {
        "order_cases": {
            "total": total_cases
        }
    }
