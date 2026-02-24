from datetime import datetime

from Delivery_app_BK.models import db, DeliveryPlan, DeliveryPlanState, Team, Order
from Delivery_app_BK.services.domain.plan.plan_states import PlanStateId
from Delivery_app_BK.services.commands.order.event_emitter import emit_order_events
from Delivery_app_BK.services.commands.order.update_order_delivery_plan import (
    apply_orders_delivery_plan_change,
)
from ...context import ServiceContext
from ..base.create_instance import create_instance
from ..utils import extract_fields, build_create_result
from .plan_type_builder import build_plan_type_instances


def create_plan(ctx: ServiceContext):
    relationship_map = {
        "team_id": Team,
        "orders": Order,
        "plan_state": DeliveryPlanState,
        "state_id": DeliveryPlanState,
    }
    ctx.set_relationship_map(relationship_map)
    plan_instances = []
    order_links_map = []
    plan_type_instances = []
    route_solution_instances = []
    pending_order_events: list[dict] = []

    for field_set in extract_fields(ctx):
        plan_type = field_set.get("plan_type", None)
        new_order_links = field_set.pop("new_order_links", None)
        order_ids = field_set.pop("order_ids", None)
        linked_order_ids = _resolve_linked_order_ids(new_order_links, order_ids)
        fields_plan_type = field_set.pop(plan_type, None)
        _normalize_plan_dates(field_set)
        plan_instance:DeliveryPlan = create_instance(ctx, DeliveryPlan, field_set)
        plan_type_instance, extra_instances = build_plan_type_instances(
            ctx, plan_type, fields_plan_type, plan_instance
        )
        if 'state_id' not in field_set:
            plan_instance.state_id = PlanStateId.OPEN

        order_links_map.append((plan_instance, linked_order_ids))
        plan_instances.append(plan_instance)
        plan_type_instances.append(plan_type_instance)
        route_solution_instances.extend(extra_instances)

    db.session.add_all(plan_instances)
    db.session.add_all(plan_type_instances)
    if route_solution_instances:
        db.session.add_all(route_solution_instances)
    db.session.flush()

    # Assign orders to plans using batch delivery-plan-change semantics.
    for plan_instance, linked_order_ids in order_links_map:
        if not linked_order_ids:
            continue
        outcome = apply_orders_delivery_plan_change(ctx, linked_order_ids, plan_instance.id)
        pending_order_events.extend(outcome["pending_events"])

    plan_results = build_create_result(ctx, plan_instances)
    plan_type_results = build_create_result(ctx, plan_type_instances)
    route_solution_results = None
    if route_solution_instances:
        route_solution_results = build_create_result(
            ctx,
            route_solution_instances,
            extract_fields=["id", "label", "is_optimized", "is_selected"],
        )
        
    db.session.commit()
    if pending_order_events:
        emit_order_events(ctx, pending_order_events)

    result = {
        "delivery_plan": plan_results,
        "plan_type": plan_type_results,
        "route_solution": route_solution_results,
    }
    return result


def _normalize_plan_dates(fields: dict) -> None:
    start_date = fields.get("start_date")
    end_date = fields.get("end_date")

    if start_date:
        normalized = _normalize_date_start(start_date)
        if normalized:
            fields["start_date"] = normalized

    if end_date:
        normalized = _normalize_date_end(end_date)
        if normalized:
            fields["end_date"] = normalized


def _normalize_date_start(value):
    parsed = _parse_datetime(value)
    if parsed:
        return parsed.replace(hour=0, minute=0, second=0, microsecond=0)
    return value


def _normalize_date_end(value):
    parsed = _parse_datetime(value)
    if parsed:
        return parsed.replace(hour=23, minute=59, second=59, microsecond=0)
    return value


def _parse_datetime(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        parsed = value.strip().replace("Z", "+00:00")
        if parsed:
            try:
                return datetime.fromisoformat(parsed)
            except ValueError:
                return None
    return None


def _resolve_linked_order_ids(
    new_order_links: list[int] | None,
    order_ids: list[int] | None,
) -> list[int]:
    if isinstance(new_order_links, list):
        return new_order_links
    if isinstance(order_ids, list):
        return order_ids
    return []
