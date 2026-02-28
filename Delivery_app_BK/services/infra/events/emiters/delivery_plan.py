from typing import Iterable

from Delivery_app_BK.models import DeliveryPlanEvent, db
from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.infra.events import get_event_bus


def emit_delivery_plan_events(
    ctx: ServiceContext,
    events: Iterable[dict],
) -> list[DeliveryPlanEvent]:
    event_rows: list[DeliveryPlanEvent] = []
    actor_id = ctx.user_id if ctx.user_id else None

    for event in events:
        delivery_plan_id = event.get("delivery_plan_id")
        event_name = event.get("event_name")
        if not delivery_plan_id or not event_name:
            continue

        payload = event.get("payload")
        if not isinstance(payload, dict):
            payload = {}

        row = DeliveryPlanEvent(
            delivery_plan_id=delivery_plan_id,
            event_name=event_name,
            payload=payload,
            actor_id=event.get("actor_id", actor_id),
            team_id=event.get("team_id", ctx.team_id),
        )
        db.session.add(row)
        event_rows.append(row)

    if not event_rows:
        return []

    db.session.flush()
    db.session.commit()

    event_bus = get_event_bus()
    for event_row in event_rows:
        event_bus.publish(event_row)

    return event_rows
