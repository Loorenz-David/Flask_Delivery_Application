from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from Delivery_app_BK.route_optimization.constants.is_optimized import (
    IS_OPTIMIZED_OPTIMIZE,
)
from Delivery_app_BK.route_optimization.constants.skip_reason_messages import (
    resolve_skip_reason_message,
)

from Delivery_app_BK.models import RouteSolutionStop, RouteSolution,db
from Delivery_app_BK.route_optimization.domain.models import (
    OptimizationContext,
    OptimizationRequest,
    OptimizationResult,
)
from Delivery_app_BK.services.commands.utils import generate_client_id


def persist_solution(
    context: OptimizationContext,
    request: OptimizationRequest,
    result: OptimizationResult,
    provider_name: str,
) -> Dict[str, Any]:
    route_solution = context.route_solution
    route_solution.algorithm = provider_name
    route_solution.score = calculate_score(result)
    route_solution.total_distance_meters = result.total_distance_meters
    route_solution.total_travel_time_seconds = result.total_duration_seconds
    route_solution.expected_start_time = _parse_datetime(result.expected_start_time)
    route_solution.expected_end_time = _parse_datetime(result.expected_end_time)
    route_solution.start_leg_polyline = None
    route_solution.end_leg_polyline = None

    route_solution.start_location = request.start_location
    route_solution.end_location = request.end_location
    
    route_solution.is_optimized = IS_OPTIMIZED_OPTIMIZE
    route_solution.has_route_warnings = False
    route_solution.route_warnings = None

    stop_lookup = {stop.order_id: stop for stop in (route_solution.stops or [])}
    stop_payloads: List[Dict[str, Any]] = []
    skipped_payloads: List[Dict[str, Any]] = []
    payload_refs: List[tuple[Dict[str, Any], RouteSolutionStop]] = []
    routed_stop_instances: list[RouteSolutionStop] = []

    for stop in result.stops:
        stop_instance = stop_lookup.get(stop.order_id)
        if not stop_instance:
            stop_instance = RouteSolutionStop(
                client_id=generate_client_id('route_stop'),
                route_solution_id=route_solution.id,
                order_id=stop.order_id,
                team_id=context.local_delivery_plan.team_id,
            )
            route_solution.stops.append(stop_instance)
            db.session.add(stop_instance)
        if not stop_instance.client_id:
            stop_instance.client_id = generate_client_id('route_stop')
        stop_instance.stop_order = stop.stop_order
        stop_instance.expected_arrival_time = stop.expected_arrival_time
        stop_instance.in_range = stop.in_range
        stop_instance.reason_was_skipped = None
        stop_instance.eta_status = "valid"
        stop_instance.has_constraint_violation = False
        stop_instance.constraint_warnings = None
        stop_instance.to_next_polyline = None
        routed_stop_instances.append(stop_instance)
        payload = {
            "id": stop_instance.id,
            "client_id": stop_instance.client_id,
            "order_id": stop_instance.order_id,
            "stop_order": stop_instance.stop_order,
            "expected_arrival_time": _serialize_datetime(stop_instance.expected_arrival_time),
            "in_range": stop_instance.in_range,
            "eta_status": stop_instance.eta_status,
            "reason_was_skipped": stop_instance.reason_was_skipped,
            "route_solution_id": route_solution.id,
            "has_constraint_violation": stop_instance.has_constraint_violation,
            "constraint_warnings":stop_instance.constraint_warnings,
            "to_next_polyline": stop_instance.to_next_polyline,

        }
        stop_payloads.append(payload)
        payload_refs.append((payload, stop_instance))

    last_stop_order = max(
        (p["stop_order"] for p in stop_payloads),
        default=0,
    )

    for index, skipped in enumerate(result.skipped):

        stop_instance = stop_lookup.get(skipped.order_id)
        if not stop_instance:
            stop_instance = RouteSolutionStop(
                client_id=generate_client_id('route_stop'),
                route_solution_id=route_solution.id,
                order_id=skipped.order_id,
                team_id=context.local_delivery_plan.team_id,
            )
            route_solution.stops.append(stop_instance)
            db.session.add(stop_instance)
        if not stop_instance.client_id:
            stop_instance.client_id = generate_client_id('route_stop')
        stop_instance.in_range = False
        stop_instance.expected_arrival_time = None
        stop_instance.reason_was_skipped = resolve_skip_reason_message(skipped.reason)
        stop_instance.eta_status = "stale"
        stop_instance.has_constraint_violation = False
        stop_instance.constraint_warnings = None
        stop_instance.to_next_polyline = None
        stop_instance.stop_order = last_stop_order + index + 1
        payload = {
            "id": stop_instance.id,
            "client_id": stop_instance.client_id,
            "order_id": stop_instance.order_id,
            "stop_order": stop_instance.stop_order,
            "expected_arrival_time": _serialize_datetime(stop_instance.expected_arrival_time),
            "in_range": stop_instance.in_range,
            "eta_status": stop_instance.eta_status,
            "reason_was_skipped": stop_instance.reason_was_skipped,
            "route_solution_id": route_solution.id,
            "has_constraint_violation": stop_instance.has_constraint_violation,
            "constraint_warnings":stop_instance.constraint_warnings,
            "to_next_polyline": stop_instance.to_next_polyline,
            
        }
        skipped_payloads.append(payload)
        payload_refs.append((payload, stop_instance))



    if request.populate_transition_polylines:
        _assign_segment_polylines(
            route_solution=route_solution,
            routed_stops=routed_stop_instances,
            transition_polylines=result.transition_polylines or [],
        )

    db.session.add(route_solution)
    db.session.flush()

    for payload, stop_instance in payload_refs:
        payload["id"] = stop_instance.id
        payload["to_next_polyline"] = stop_instance.to_next_polyline

    db.session.commit()

    if context.return_shape == "map_ids_object":
        route_solution_payload = _build_route_solution_payload(route_solution)
        return {
            "route_solution": {
                route_solution.client_id: route_solution_payload,
            },
            "route_solution_stop": {
                payload["client_id"]: payload for payload in stop_payloads
            },
            "route_solution_stop_skipped": {
                payload["client_id"]: payload for payload in skipped_payloads
            },
        }

    return {
        "route_solution": {},
        "route_solution_stop": [],
        "route_solution_id": route_solution.id,
        "total_distance_meters": result.total_distance_meters,
        "total_duration_seconds": result.total_duration_seconds,
        "expected_start_time": result.expected_start_time,
        "expected_end_time": result.expected_end_time,
        "stops": stop_payloads,
        "skipped": skipped_payloads,
    }


def _build_route_solution_payload(route_solution:RouteSolution) -> Dict[str, Any]:
    return {
        "id": route_solution.id,
        "client_id": route_solution.client_id,
        "_representation": "full",
        "label": route_solution.label,
        "is_selected": route_solution.is_selected,
        "is_optimized": route_solution.is_optimized,
        "stop_count": route_solution.stop_count,
        "total_distance_meters": route_solution.total_distance_meters,
        "total_travel_time_seconds": route_solution.total_travel_time_seconds,
        "expected_start_time": _serialize_datetime(route_solution.expected_start_time),
        "expected_end_time": _serialize_datetime(route_solution.expected_end_time),
        "start_leg_polyline": route_solution.start_leg_polyline,
        "end_leg_polyline": route_solution.end_leg_polyline,
        "start_location": route_solution.start_location,
        "end_location": route_solution.end_location,
        "set_start_time": route_solution.set_start_time,
        "set_end_time": route_solution.set_end_time,
        "driver_id": route_solution.driver_id,
        "local_delivery_plan_id": route_solution.local_delivery_plan_id,
        "has_route_warnings": route_solution.has_route_warnings,
        "route_warnings": route_solution.route_warnings,
    }


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = str(value).replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(parsed)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _serialize_datetime(value: datetime | None) -> str | None:
    if not value:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat().replace("+00:00", "Z")


def _assign_segment_polylines(
    route_solution: RouteSolution,
    routed_stops: list[RouteSolutionStop],
    transition_polylines: list[Optional[str]],
) -> None:
    if not transition_polylines:
        route_solution.start_leg_polyline = None
        route_solution.end_leg_polyline = None
        for stop in routed_stops:
            stop.to_next_polyline = None
        return

    ordered_stops = sorted(
        routed_stops,
        key=lambda stop: stop.stop_order if stop.stop_order is not None else 0,
    )

    route_solution.start_leg_polyline = transition_polylines[0] if transition_polylines else None
    route_solution.end_leg_polyline = (
        transition_polylines[len(ordered_stops)]
        if len(transition_polylines) > len(ordered_stops)
        else None
    )

    for idx, stop in enumerate(ordered_stops):
        stop.to_next_polyline = (
            transition_polylines[idx + 1]
            if idx + 1 < len(ordered_stops)
            and len(transition_polylines) > (idx + 1)
            else None
        )


def calculate_score(result:OptimizationResult):
    score = (
        result.total_distance_meters
        + 60 * result.total_duration_seconds
        + 10_000 * len(result.skipped)
    )

    return score
