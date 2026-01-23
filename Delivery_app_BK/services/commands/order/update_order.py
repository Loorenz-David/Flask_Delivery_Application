from Delivery_app_BK.models import (
    db,
    Order,
    DeliveryPlan,
    OrderState,
)
from ...context import ServiceContext
from ..base.update_instance import update_instance
from ..utils import extract_targets


RELATIONSHIP_KEYS = {
    "items",
    "order_chats",
    "state",
    "state_history",
    "delivery_plan",
    "team",
}


def update_order(ctx: ServiceContext):
    ctx.set_relationship_map( {
        "order_state_id": OrderState,
        "delivery_plan_id": DeliveryPlan,
    })
    instances = []
    for target in extract_targets(ctx):
        fields = dict(target["fields"] or {})
        for key in RELATIONSHIP_KEYS:
            fields.pop(key, None)
        instance = update_instance(ctx, Order, fields, target["target_id"])
        instances.append(instance.id)
    db.session.commit()
    return instances
