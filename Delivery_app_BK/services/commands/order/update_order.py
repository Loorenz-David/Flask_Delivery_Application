from datetime import datetime
from typing import Any
from sqlalchemy.orm.exc import NoResultFound

from Delivery_app_BK.models import (
    db,
    Order,
    DeliveryPlan,
    Team,
    OrderState,
)
from Delivery_app_BK.services.utils import to_datetime
from ...context import ServiceContext
from ...domain.order.order_events import OrderEvent
from ...queries.get_instance import get_instance
from ..utils import extract_targets
from ..utils.inject_fields import inject_fields
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
        "team_id":Team,
        "order_state_id": OrderState,
        "delivery_plan_id": DeliveryPlan,
    })
    targets = extract_targets(ctx)
    instances, pending_events = apply_order_updates(ctx, targets)
    db.session.commit()
    emit_order_events(ctx, pending_events)
    return instances


def apply_order_updates(
    ctx: ServiceContext,
    targets: list[dict[str, Any]],
) -> tuple[list[int], list[dict[str, Any]]]:
    
   
    from pprint import pprint
    print('rel map')
    pprint(ctx.relationship_map)
    instances: list[int] = []
    pending_events: list[dict[str, Any]] = []
    existing_orders = _resolve_orders_by_targets(ctx, targets)

    for target in targets:
        target_id = target["target_id"]
        existing: Order = existing_orders[target_id]
        # Reuse team-safety checks without triggering another DB query.
        get_instance(ctx, Order, existing)

        old_earliest: datetime = existing.earliest_delivery_date
        old_latest: datetime = existing.latest_delivery_date
        old_plan_id = existing.delivery_plan_id

        fields = dict(target["fields"] or {})
        for key in RELATIONSHIP_KEYS:
            fields.pop(key, None)

        inject_fields(ctx, existing, fields)
        instances.append(existing.id)

        new_earliest = to_datetime(existing.earliest_delivery_date)
        new_latest = to_datetime(existing.latest_delivery_date)

        if old_earliest != new_earliest or old_latest != new_latest:
            pending_events.append(
                {
                    "order_id": existing.id,
                    "event_name": OrderEvent.DELIVERY_WINDOW_RESCHEDULED_BY_USER.value,
                    "payload": {
                        "old_earliest_delivery_date": old_earliest.isoformat() if old_earliest else None,
                        "old_latest_delivery_date": old_latest.isoformat() if old_latest else None,
                        "new_earliest_delivery_date": new_earliest.isoformat() if new_earliest else None,
                        "new_latest_delivery_date": new_latest.isoformat() if new_latest else None,
                    },
                    "team_id": existing.team_id,
                }
            )

        if old_plan_id != existing.delivery_plan_id:
            pending_events.append(
                {
                    "order_id": existing.id,
                    "event_name": OrderEvent.DELIVERY_PLAN_CHANGED.value,
                    "payload": {
                        "old_delivery_plan_id": old_plan_id,
                        "new_delivery_plan_id": existing.delivery_plan_id,
                    },
                    "team_id": existing.team_id,
                }
            )

    return instances, pending_events


def _resolve_orders_by_targets(
    ctx: ServiceContext,
    targets: list[dict[str, Any]],
) -> dict[int | str, Order]:
    target_ids = [target["target_id"] for target in targets]
    int_ids = [value for value in target_ids if isinstance(value, int)]
    client_ids = [value for value in target_ids if isinstance(value, str)]

    orders_by_id: dict[int, Order] = {}
    orders_by_client_id: dict[str, Order] = {}

    if int_ids:
        for order in db.session.query(Order).filter(Order.id.in_(int_ids)).all():
            orders_by_id[order.id] = order

    if client_ids:
        for order in db.session.query(Order).filter(Order.client_id.in_(client_ids)).all():
            orders_by_client_id[order.client_id] = order

    resolved: dict[int | str, Order] = {}
    missing: list[int | str] = []
    for target_id in target_ids:
        order = orders_by_id.get(target_id) if isinstance(target_id, int) else orders_by_client_id.get(target_id)
        if order is None:
            missing.append(target_id)
            continue
        resolved[target_id] = order

    if missing:
        raise NoResultFound(f"Orders not found: {missing}")

    return resolved
