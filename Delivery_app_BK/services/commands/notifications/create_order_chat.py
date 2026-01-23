from Delivery_app_BK.models import db, OrderChat, Order, Team

from ...context import ServiceContext
from ..base.create_instance import create_instance
from ..utils import extract_fields, build_create_result


def create_order_chat(ctx: ServiceContext):
    relationship_map = {
        "team_id": Team,
        "order_id": Order,
        "order": Order,
    }
    ctx.set_relationship_map(relationship_map)
    instances = []

    for field_set in extract_fields(ctx):
        instance = create_instance(ctx, OrderChat, dict(field_set))
        instances.append(instance)

    db.session.add_all(instances)
    db.session.flush()
    result = build_create_result(ctx, instances)
    db.session.commit()
    return {'order_chat':result}
