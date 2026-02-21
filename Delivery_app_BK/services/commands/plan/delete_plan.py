from Delivery_app_BK.models import db, DeliveryPlan
from ...context import ServiceContext
from ..base.delete_instance import delete_instance
from ..utils import extract_ids


def delete_plan(ctx: ServiceContext):
    instances = []
    for target_id in extract_ids(ctx):
        instances.append(delete_instance(ctx, DeliveryPlan, target_id))
    db.session.commit()
    return instances
