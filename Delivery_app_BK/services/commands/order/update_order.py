from datetime import datetime
from typing import Any
from sqlalchemy.orm.exc import NoResultFound

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import (
    db,
    Order,
)
from Delivery_app_BK.services.infra.events.builders.order import (
    build_delivery_window_rescheduled_by_user_event,
)
from Delivery_app_BK.services.infra.events.emiters.order import emit_order_events
from Delivery_app_BK.services.utils import model_requires_team, require_team_id, to_datetime
from ...context import ServiceContext
from ..utils import extract_targets
from ..utils.inject_fields import inject_fields


FORBIDDEN_FIELD_KEYS = {
    "order_state_id",
    "delivery_plan_id",
}

FORBIDDEN_RELATIONSHIP_KEYS = {
    "state",
    "order_state",
    "state_history",
    "delivery_plan",
}

MUTABLE_FIELDS = {
    "order_plan_objective",
    "reference_number",
    "external_order_id",
    "external_source",
    "tracking_number",
    "tracking_link",
    "client_first_name",
    "client_last_name",
    "client_email",
    "client_primary_phone",
    "client_secondary_phone",
    "client_address",
    "marketing_messages",
    "earliest_delivery_date",
    "latest_delivery_date",
    "preferred_time_start",
    "preferred_time_end",
}


def update_order(ctx: ServiceContext):
    ctx.set_relationship_map({})
    targets = extract_targets(ctx)
    _validate_targets_update_fields(targets)
    instances, pending_events = apply_order_updates(ctx, targets)
    db.session.commit()
    emit_order_events(ctx, pending_events)
    return instances


def apply_order_updates(
    ctx: ServiceContext,
    targets: list[dict[str, Any]],
) -> tuple[list[int], list[dict[str, Any]]]:
    
    updated_order_ids: list[int] = []
    pending_events: list[dict[str, Any]] = []
    existing_orders = _resolve_orders_by_targets(ctx, targets)

    for order_target in targets:
        target_id = order_target["target_id"]
        existing: Order = existing_orders[target_id]

        old_earliest: datetime = to_datetime(existing.earliest_delivery_date)
        old_latest: datetime = to_datetime(existing.latest_delivery_date)

        fields_to_apply = _build_mutable_fields(order_target["fields"])
        if fields_to_apply:
            inject_fields(ctx, existing, fields_to_apply)

        updated_order_ids.append(existing.id)

        new_earliest = to_datetime(existing.earliest_delivery_date)
        new_latest = to_datetime(existing.latest_delivery_date)

        if old_earliest != new_earliest or old_latest != new_latest:
            pending_events.append(
                build_delivery_window_rescheduled_by_user_event(
                    order_instance=existing,
                    old_earliest=old_earliest,
                    old_latest=old_latest,
                    new_earliest=new_earliest,
                    new_latest=new_latest,
                )
            )

    return updated_order_ids, pending_events


def _validate_targets_update_fields(targets: list[dict[str, Any]]) -> None:
    for target in targets:
        target_id = target["target_id"]
        fields = target.get("fields") or {}
        field_keys = set(fields.keys())

        forbidden_keys = sorted(
            field_keys & (FORBIDDEN_FIELD_KEYS | FORBIDDEN_RELATIONSHIP_KEYS)
        )
        if forbidden_keys:
            raise ValidationFailed(
                f"Target '{target_id}' contains forbidden fields for this endpoint: {forbidden_keys}"
            )

        unsupported_keys = sorted(field_keys - MUTABLE_FIELDS)
        if unsupported_keys:
            raise ValidationFailed(
                f"Target '{target_id}' contains unsupported fields for this endpoint: {unsupported_keys}"
            )


def _build_mutable_fields(raw_fields: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in raw_fields.items() if key in MUTABLE_FIELDS}


def _resolve_orders_by_targets(
    ctx: ServiceContext,
    targets: list[dict[str, Any]],
) -> dict[int | str, Order]:
    target_ids = [target["target_id"] for target in targets]
    int_ids = [value for value in target_ids if isinstance(value, int)]
    client_ids = [value for value in target_ids if isinstance(value, str)]

    orders_by_id: dict[int, Order] = {}
    orders_by_client_id: dict[str, Order] = {}
    team_id = None

    if model_requires_team(Order) and ctx.check_team_id:
        team_id = require_team_id(ctx)

    if int_ids:
        query = db.session.query(Order).filter(Order.id.in_(int_ids))
        if team_id is not None:
            query = query.filter(Order.team_id == team_id)
        for order in query.all():
            orders_by_id[order.id] = order

    if client_ids:
        query = db.session.query(Order).filter(Order.client_id.in_(client_ids))
        if team_id is not None:
            query = query.filter(Order.team_id == team_id)
        for order in query.all():
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
