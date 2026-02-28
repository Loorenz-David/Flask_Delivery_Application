import logging

from Delivery_app_BK.models import db
from Delivery_app_BK.services.commands.plan.local_delivery.route_solution.update_route_solution_from_plan import (
    update_route_solution_from_plan,
)
from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.requests.plan.local_delivery.update_settings import (
    LocalDeliverySettingsRequest,
    RouteSolutionPatchRequest,
    parse_update_local_delivery_settings_request,
)

from ..events import emit_pending_delivery_plan_events
from .loader import load_local_delivery_settings_entities
from ..update_plan import apply_delivery_plan_patch
from .response_builder import build_local_delivery_settings_response

logger = logging.getLogger(__name__)


def update_local_delivery_settings(ctx: ServiceContext) -> dict:
    incoming_data = ctx.incoming_data or {}
    _warn_if_driver_conflict(ctx, incoming_data)
    request: LocalDeliverySettingsRequest = parse_update_local_delivery_settings_request(
        incoming_data
    )
 
    local_delivery_plan, delivery_plan, route_solution = load_local_delivery_settings_entities(
        ctx=ctx,
        request=request,
    )
   

    previous_start, previous_end, pending_plan_events = apply_delivery_plan_patch(
        delivery_plan=delivery_plan,
        patch=request.delivery_plan,
    )
  
   

    route_updates = _build_route_solution_updates(request.route_solution)
    effective_time_zone = ctx.time_zone
    route_solution, stops_changed, original_route_solution = update_route_solution_from_plan(
        route_solution=route_solution,
        updates=route_updates,
        plan_start=delivery_plan.start_date,
        plan_end=delivery_plan.end_date,
        previous_plan_start=previous_start,
        previous_plan_end=previous_end,
        create_variant_on_save=request.create_variant_on_save,
        time_zone=effective_time_zone,
    )
    plan_window_changed = (
        previous_start != delivery_plan.start_date
        or previous_end != delivery_plan.end_date
    )
    route_patch_requested = _has_route_solution_patch(request.route_solution)
    route_solution_changed = (
        plan_window_changed
        or route_patch_requested
        or original_route_solution is not None
        or stops_changed
    )

    db.session.add(delivery_plan)
    db.session.add(local_delivery_plan)
    db.session.add(route_solution)
    if original_route_solution is not None:
        db.session.add(original_route_solution)
    if stops_changed:
        db.session.add_all(route_solution.stops or [])
    db.session.commit()

   

    emit_pending_delivery_plan_events(ctx, pending_plan_events)
   

    return build_local_delivery_settings_response(
        ctx=ctx,
        route_solution=route_solution,
        stops_changed=stops_changed,
        route_solution_changed=route_solution_changed,
    )


def _build_route_solution_updates(route_patch: RouteSolutionPatchRequest) -> dict:
    updates: dict = {"route_solution_id": route_patch.route_solution_id}

    if route_patch.has_start_location:
        updates["start_location"] = route_patch.start_location
    if route_patch.has_end_location:
        updates["end_location"] = route_patch.end_location
    if route_patch.has_set_start_time:
        updates["set_start_time"] = route_patch.set_start_time
    if route_patch.has_set_end_time:
        updates["set_end_time"] = route_patch.set_end_time
    if route_patch.has_route_end_strategy:
        updates["route_end_strategy"] = route_patch.route_end_strategy
    if route_patch.has_driver_id:
        updates["driver_id"] = route_patch.driver_id

    return updates


def _warn_if_driver_conflict(ctx: ServiceContext, raw: dict) -> None:
    if not isinstance(raw, dict):
        return
    local_payload = raw.get("local_delivery_plan") if isinstance(raw.get("local_delivery_plan"), dict) else {}
    route_payload = raw.get("route_solution") if isinstance(raw.get("route_solution"), dict) else {}
    if "driver_id" not in local_payload or "driver_id" not in route_payload:
        return
    if local_payload.get("driver_id") != route_payload.get("driver_id"):
        ctx.set_warning(
            "route_solution.driver_id overrides local_delivery_plan.driver_id in this update."
        )


def _has_route_solution_patch(route_patch: RouteSolutionPatchRequest) -> bool:
    return any(
        [
            route_patch.has_start_location,
            route_patch.has_end_location,
            route_patch.has_set_start_time,
            route_patch.has_set_end_time,
            route_patch.has_route_end_strategy,
            route_patch.has_driver_id,
        ]
    )
