from Delivery_app_BK.models import db, OrderCase
from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.commands.base.update_instance import update_instance
from Delivery_app_BK.services.commands.utils import extract_targets


def update_order_case_state(ctx: ServiceContext):
    instances = []
    for target in extract_targets(ctx):
        state = (target.get("fields") or {}).get("state")
        if state is None:
            raise ValidationFailed("Missing 'state' in fields payload.")
        instance = update_instance(
            ctx,
            OrderCase,
            {"state": state},
            target["target_id"],
        )
        instances.append(instance.id)
    db.session.commit()
    return instances
