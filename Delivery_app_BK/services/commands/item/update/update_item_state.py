from Delivery_app_BK.models import db, ItemState
from ....context import ServiceContext
from ...base.update_instance import update_instance
from ...utils import extract_targets


def update_item_state(ctx: ServiceContext):
    instances = []
    for target in extract_targets(ctx):
        instance = update_instance(ctx, ItemState, target["fields"], target["target_id"])
        instances.append(instance.id)
    db.session.commit()
    return instances
