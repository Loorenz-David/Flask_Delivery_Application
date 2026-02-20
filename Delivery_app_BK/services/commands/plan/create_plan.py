from datetime import datetime, time as time_cls

from Delivery_app_BK.models import db, DeliveryPlan, DeliveryPlanState, Team, Order
from Delivery_app_BK.services.domain.plan.plan_states import PlanStateId
from ...context import ServiceContext
from ..base.create_instance import create_instance
from ..utils import extract_fields, build_create_result
from .plan_type_builder import build_plan_type_instances


def create_plan(ctx: ServiceContext):
    relationship_map = {
        "team_id": Team,
        "orders": Order,
        "plan_state": DeliveryPlanState,
        "state_id": DeliveryPlanState
    }
    ctx.set_relationship_map(relationship_map)
    plan_instances = []
    plan_type_instances = []
    route_solution_instances = []

    for field_set in extract_fields(ctx):
        plan_type = field_set.get("plan_type", None)
        fields_plan_type = field_set.pop(plan_type, None)
        _normalize_plan_dates(field_set)
        plan_instance:DeliveryPlan = create_instance(ctx, DeliveryPlan, field_set)
        plan_type_instance, extra_instances = build_plan_type_instances(
            ctx, plan_type, fields_plan_type, plan_instance
        )
        if 'state_id' not in field_set:
            plan_instance.state_id = PlanStateId.OPEN

        plan_instances.append(plan_instance)
        plan_type_instances.append(plan_type_instance)
        route_solution_instances.extend(extra_instances)

    db.session.add_all(plan_instances)
    db.session.add_all(plan_type_instances)
    if route_solution_instances:
        db.session.add_all(route_solution_instances)
    db.session.flush()

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
