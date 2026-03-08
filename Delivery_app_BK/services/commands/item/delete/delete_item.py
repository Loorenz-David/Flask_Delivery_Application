from Delivery_app_BK.models import db, Item, Order
from ....context import ServiceContext
from ...base.delete_instance import delete_instance
from ...utils import extract_ids
from ....queries.get_instance import get_instance
from Delivery_app_BK.services.domain.item.order_item_freshness import (
    touch_orders_items_updated_at,
)


def delete_item(ctx: ServiceContext):
    instances = []
    touched_orders: list[Order] = []
    for target_id in extract_ids(ctx):
        item = get_instance(ctx, Item, target_id)
        if item.order is not None:
            touched_orders.append(item.order)
        instances.append(delete_instance(ctx, Item, target_id))
    touch_orders_items_updated_at(touched_orders)
    db.session.commit()
    return instances
