from datetime import datetime

from Delivery_app_BK.models import (
    db,
    Order,
    DeliveryPlan,
    OrderState,
)
from Delivery_app_BK.services.utils import to_datetime
from ...context import ServiceContext
from ...domain.order.order_events import OrderEvent
from ...queries.get_instance import get_instance
from ..base.update_instance import update_instance
from ..utils import extract_targets
from .event_emitter import emit_order_events


RELATIONSHIP_KEYS = {
    "items",
    "order_cases",
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
    pending_events: list[dict] = []
    for target in extract_targets(ctx):
        existing: Order = get_instance(ctx, Order, target["target_id"])
        old_earliest:datetime = existing.earliest_delivery_date
        old_latest:datetime = existing.latest_delivery_date
        old_plan_id = existing.delivery_plan_id

       
        fields = dict(target["fields"] or {})
        for key in RELATIONSHIP_KEYS:
            fields.pop(key, None)
        instance: Order = update_instance(ctx, Order, fields, target["target_id"])
        instances.append(instance.id)

        new_earliest = to_datetime(fields.get("earliest_delivery_date"))
        new_latest = to_datetime(fields.get("latest_delivery_date"))

        if old_earliest != new_earliest or old_latest != new_latest:
            
            pending_events.append(
                {
                    "order_id": instance.id,
                    "event_name": OrderEvent.DELIVERY_WINDOW_RESCHEDULED_BY_USER.value,
                    "payload": {
                        "old_earliest_delivery_date": old_earliest.isoformat() if old_earliest else None,
                        "old_latest_delivery_date": old_latest.isoformat() if old_latest else None,
                        "new_earliest_delivery_date": new_earliest.isoformat() if new_earliest else None,
                        "new_latest_delivery_date": new_latest.isoformat() if new_latest else None,
                    },
                    "team_id": instance.team_id,
                }
            )


        if old_plan_id != instance.delivery_plan_id:
            pending_events.append(
                {
                    "order_id": instance.id,
                    "event_name": OrderEvent.DELIVERY_PLAN_CHANGED.value,
                    "payload": {
                        "old_delivery_plan_id": old_plan_id,
                        "new_delivery_plan_id": instance.delivery_plan_id,
                    },
                    "team_id": instance.team_id,
                }
            )

        

            
    db.session.commit()
    emit_order_events(ctx, pending_events)
    return instances
