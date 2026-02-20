from Delivery_app_BK.models import db, OrderCase, Order, Team, User
from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.commands.base.update_instance import update_instance
from Delivery_app_BK.services.commands.utils import extract_targets


def update_order_case(ctx: ServiceContext):
    relationship_map = {
        "team_id": Team,
        "order_id": Order,
        "created_by": User,
    }
    ctx.set_relationship_map(relationship_map)
    instances = []
    for target in extract_targets(ctx):
        instance = update_instance(
            ctx, OrderCase, target["fields"], target["target_id"]
        )
        instances.append(instance.id)
    db.session.commit()
    return instances
