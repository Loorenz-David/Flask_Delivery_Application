from Delivery_app_BK.models import db, OrderChat, Order, Team

from ...context import ServiceContext
from ..base.update_instance import update_instance
from ..utils import extract_targets


def update_order_chat(ctx: ServiceContext):
    relationship_map = {
        "team_id": Team,
        "order_id": Order,
        "order": Order,
    }
    ctx.set_relationship_map(relationship_map)
    instances = []
    for target in extract_targets(ctx):
        instance = update_instance(
            ctx, OrderChat, target["fields"], target["target_id"]
        )
        instances.append(instance.id)
    db.session.commit()
    return instances
