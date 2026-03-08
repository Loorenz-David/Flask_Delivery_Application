from Delivery_app_BK.models import (
    db,
    Item,
    Order,
    ItemState,
    ItemPosition,
    Team
)
from ....context import ServiceContext
from ...base.create_instance import create_instance
from ...utils import extract_fields, build_create_result
from Delivery_app_BK.services.domain.item.order_item_freshness import (
    touch_orders_items_updated_at,
)


def create_item(ctx: ServiceContext):
    relationship_map = {
        "order_id": Order,
        "item_state_id": ItemState,
        "item_position_id": ItemPosition,
        "team_id": Team
    }
    ctx.set_relationship_map(relationship_map)
    instances = []
    touched_orders: list[Order] = []

    for field_set in extract_fields(ctx):

        instance = create_instance(ctx, Item, dict(field_set))
        instances.append(instance)
        if instance.order is not None:
            touched_orders.append(instance.order)

    db.session.add_all(instances)
    touch_orders_items_updated_at(touched_orders)
    db.session.flush()
    result = build_create_result(ctx, instances)
    db.session.commit()
    return {"item":result}
