from Delivery_app_BK.models import db, Item, Order,ItemState, ItemPosition
from ....context import ServiceContext
from ...base.update_instance import update_instance
from ...utils import extract_targets


def update_item(ctx: ServiceContext):
    relationship_map = {
        "order_id": Order,
        "item_state_id": ItemState,
        "item_position_id": ItemPosition,
    }
    ctx.set_relationship_map(relationship_map)
    instances = []
    for target in extract_targets(ctx):
        instance = update_instance(ctx, Item, target["fields"], target["target_id"])
        instances.append(instance.id)
    db.session.commit()
    return instances
