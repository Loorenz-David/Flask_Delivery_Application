from Delivery_app_BK.models import db, Item, Order,ItemState, ItemPosition
from ....context import ServiceContext
from ...base.update_instance import update_instance
from ...utils import extract_targets
from ....queries.get_instance import get_instance
from Delivery_app_BK.services.domain.item.order_item_freshness import (
    touch_orders_items_updated_at,
)


def update_item(ctx: ServiceContext):
    relationship_map = {
        "order_id": Order,
        "item_state_id": ItemState,
        "item_position_id": ItemPosition,
    }
    ctx.set_relationship_map(relationship_map)
    instances = []
    touched_orders: list[Order] = []
    for target in extract_targets(ctx):
        existing_item = get_instance(ctx, Item, target["target_id"])
        previous_order = existing_item.order
        instance = update_instance(ctx, Item, target["fields"], target["target_id"])
        instances.append(instance.id)
        if previous_order is not None:
            touched_orders.append(previous_order)
        if instance.order is not None:
            touched_orders.append(instance.order)
    touch_orders_items_updated_at(touched_orders)
    db.session.commit()
    return instances
