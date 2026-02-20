from datetime import datetime, timezone

from Delivery_app_BK.services.commands.plan.event_emitter import emit_delivery_plan_events
from Delivery_app_BK.services.domain.plan.plan_events import DeliveryPlanEvent

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import DeliveryPlan, LocalDeliveryPlan, RouteSolution, db

from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.queries.get_instance import get_instance
from Delivery_app_BK.services.queries.route_solutions import (
    serialize_route_solution_stops,
    serialize_route_solutions,
)
from Delivery_app_BK.services.commands.plan.local_delivery.update_local_delivery_plan import (
    update_local_delivery_plan,
)
from Delivery_app_BK.services.commands.route_solution.update_route_solution_from_plan import (
    update_route_solution_from_plan,
)



def update_local_delivery_plan_settings(ctx: ServiceContext):
    incoming_data = ctx.incoming_data or {}
    local_delivery_plan_id = incoming_data.get("local_delivery_plan_id")
    if not local_delivery_plan_id:
        raise ValidationFailed("local_delivery_plan_id is required.")

    local_delivery_plan: LocalDeliveryPlan = get_instance(
        ctx=ctx,
        model=LocalDeliveryPlan,
        value=local_delivery_plan_id,
    )

    delivery_plan: DeliveryPlan | None = local_delivery_plan.delivery_plan
    if not delivery_plan:
        raise ValidationFailed("Local delivery plan has no delivery plan.")

    plan_fields = incoming_data.get("delivery_plan") or {}
    route_solution_fields = incoming_data.get("route_solution") or {}
    local_delivery_fields = incoming_data.get("local_delivery_plan") or {}
    time_zone = incoming_data.get("time_zone")
    previous_start = delivery_plan.start_date
    previous_end = delivery_plan.end_date
    _apply_plan_updates(delivery_plan, plan_fields, ctx)
    _validate_plan_dates(delivery_plan.start_date, delivery_plan.end_date)

    update_local_delivery_plan(local_delivery_plan, local_delivery_fields)

    route_solution_id = (
        route_solution_fields.get("id")
        or route_solution_fields.get("route_solution_id")
    )
    if not route_solution_id:
        raise ValidationFailed("route_solution id is required.")

    route_solution: RouteSolution = get_instance(
        ctx=ctx,
        model=RouteSolution,
        value=route_solution_id,
    )

    if route_solution.local_delivery_plan_id != local_delivery_plan.id:
        raise ValidationFailed("Route solution does not belong to local delivery plan.")

    create_variant_on_save = bool(incoming_data.get("create_variant_on_save"))

    route_solution, stops_changed, original_route_solution = update_route_solution_from_plan(
        route_solution=route_solution,
        updates=route_solution_fields,
        plan_start=delivery_plan.start_date,
        plan_end=delivery_plan.end_date,
        previous_plan_start=previous_start,
        previous_plan_end=previous_end,
        create_variant_on_save=create_variant_on_save,
        time_zone = time_zone
    )

    db.session.add(delivery_plan)
    db.session.add(local_delivery_plan)
    db.session.add(route_solution)

    if original_route_solution is not None:
        db.session.add(original_route_solution)
    if stops_changed:
        db.session.add_all(route_solution.stops or [])

    db.session.commit()

    if stops_changed:
        return {
            "route_solution": serialize_route_solutions([route_solution], ctx),
            "route_solution_stops": serialize_route_solution_stops(
                list(route_solution.stops or []),
                ctx,
            ),
        }

    return {}



def _apply_plan_updates(plan: DeliveryPlan, fields: dict, ctx: ServiceContext) -> None:
    if "label" in fields:
        plan.label = fields.get("label")

    old_plan_start_date = plan.start_date
    old_plan_end_date = plan.end_date
    start_date = fields.get("start_date")
    end_date = fields.get("end_date")
    
    pending_events = []
    if start_date is not None:
        normalized = _normalize_date_start(start_date)
        plan.start_date = normalized

    if end_date is not None:
        normalized = _normalize_date_end(end_date)
        plan.end_date = normalized
    
    if old_plan_start_date != plan.start_date or old_plan_end_date != plan.end_date:
        pending_events.append(
            {   
                "delivery_plan_id": plan.id,
                "event_name": DeliveryPlanEvent.DELIVERY_PLAN_RESCHEDULED.value,
                "payload": {
                    "old_start_date": old_plan_start_date.isoformat() if old_plan_start_date else None,
                    "old_end_date": old_plan_end_date.isoformat() if old_plan_end_date else None,
                    "new_start_date": plan.start_date.isoformat() if plan.start_date else None,
                    "new_end_date": plan.end_date.isoformat() if plan.end_date else None,
                },
            }
        )
   
    emit_delivery_plan_events(ctx ,pending_events)



def _validate_plan_dates(start_date: datetime | None, end_date: datetime | None) -> None:
    start = _ensure_datetime(start_date)
    end = _ensure_datetime(end_date)

    if not start or not end:
        raise ValidationFailed("delivery plan start and end dates are required.")
    if end < start:
        raise ValidationFailed("delivery plan end date cannot be before start date.")


def _normalize_date_start(value):
    parsed = _ensure_datetime(value)
    if parsed:
        return parsed.replace(hour=0, minute=0, second=0, microsecond=0)
    return value


def _normalize_date_end(value):
    parsed = _ensure_datetime(value)
    if parsed:
        return parsed.replace(hour=23, minute=59, second=59, microsecond=0)
    return value


def _parse_datetime(value):
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        parsed = value.strip().replace("Z", "+00:00")
        if parsed:
            try:
                dt = datetime.fromisoformat(parsed)
                return dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
            except ValueError:
                return None
    return None


def _ensure_datetime(value):
    parsed = _parse_datetime(value)
    if not parsed and value is not None:
        raise ValidationFailed("delivery plan start/end date must be a valid date.")
    return parsed
