from __future__ import annotations

from datetime import datetime, time as time_cls, timezone
from typing import Dict, List, Optional

from Delivery_app_BK.models import Order, RouteSolution, RouteSolutionStop
from Delivery_app_BK.models.mixins.validation_mixins.time_warning_validation import (
    TimeWarningFactory,
)

from Delivery_app_BK.directions.domain.models import (
    DirectionsRequestBuildResult,
    DirectionsResult,
)
from Delivery_app_BK.directions.services.request_builder import (
    _parse_time_string,
)
from Delivery_app_BK.directions.services.time_window_policy import (
    apply_stop_time_window_evaluation,
    build_stop_time_warnings,
    ensure_utc,
)


def _ensure_utc(value: Optional[datetime]) -> Optional[datetime]:
    return ensure_utc(value)


def apply_directions_result(
    route_solution: RouteSolution,
    directions_result: DirectionsResult,
    orders_by_id: Dict[int, Order],
    build_result: DirectionsRequestBuildResult,
) -> list[RouteSolutionStop]:
   
    if build_result.full_recompute:
        route_solution.total_distance_meters = directions_result.total_distance_meters
        route_solution.total_travel_time_seconds = directions_result.total_duration_seconds
        if directions_result.start_time is not None:
            route_solution.expected_start_time = _ensure_utc(directions_result.start_time)

    if directions_result.end_time is not None:
        route_solution.expected_end_time = _ensure_utc(directions_result.end_time)

    route_warnings: List[dict] = []
    allowed_end = _ensure_utc(_resolve_allowed_end(route_solution))
    end_time = _ensure_utc(directions_result.end_time)
    if allowed_end and end_time and end_time > allowed_end:
        route_warnings.append(
            TimeWarningFactory.route_end_time_exceeded(
                expected_end=end_time,
                allowed_end=allowed_end,
            )
        )
    route_solution.route_warnings = route_warnings or None
    route_solution.has_route_warnings = bool(route_warnings)

    anchor_stop, affected_stops = _resolve_scope_stops(route_solution, build_result)
    stop_results_by_order_id = {
        stop_result.order_id: stop_result for stop_result in directions_result.stop_results
    }

    changed_stops: list[RouteSolutionStop] = []

    for stop in affected_stops:
        if not stop.order_id:
            continue
        stop_result = stop_results_by_order_id.get(stop.order_id)
        if stop_result is None:
            stop.expected_arrival_time = None
            stop.eta_status = "stale"
            stop.has_constraint_violation = False
            stop.constraint_warnings = None
            stop.in_range = False
            stop.reason_was_skipped = "Route timing unavailable"
            changed_stops.append(stop)
            continue

        stop.expected_arrival_time = _ensure_utc(stop_result.arrival_time)
        stop.eta_status = "estimated"
        stop.in_range = True
        stop.reason_was_skipped = None

        order_instance = orders_by_id.get(stop.order_id) or getattr(stop, "order", None)
        apply_stop_time_window_evaluation(
            stop=stop,
            order=order_instance,
            route_solution=route_solution,
            arrival_time=stop.expected_arrival_time,
        )
        changed_stops.append(stop)

    changed_stops.extend(
        _apply_segment_polylines(
            route_solution=route_solution,
            leg_polylines=directions_result.leg_polylines,
            full_recompute=build_result.full_recompute,
            anchor_stop=anchor_stop,
            affected_stops=affected_stops,
        )
    )

    return _dedupe_stops(changed_stops)


def _resolve_scope_stops(
    route_solution: RouteSolution,
    build_result: DirectionsRequestBuildResult,
) -> tuple[RouteSolutionStop | None, list[RouteSolutionStop]]:
    ordered_stops = sorted(
        [stop for stop in (route_solution.stops or []) if stop.order_id],
        key=lambda stop: stop.stop_order if stop.stop_order is not None else 0,
    )
    if build_result.full_recompute:
        return None, ordered_stops

    anchor_stop = None
    anchor_position = build_result.effective_start_position - 1
    if anchor_position >= 1:
        for stop in ordered_stops:
            if (stop.stop_order or 0) == anchor_position:
                anchor_stop = stop
                break

    affected_stops = [
        stop
        for stop in ordered_stops
        if (stop.stop_order or 0) >= build_result.effective_start_position
    ]

    return anchor_stop, affected_stops


def _apply_segment_polylines(
    route_solution: RouteSolution,
    leg_polylines: list[Optional[str]],
    full_recompute: bool,
    anchor_stop: RouteSolutionStop | None,
    affected_stops: list[RouteSolutionStop],
) -> list[RouteSolutionStop]:
    changed: list[RouteSolutionStop] = []

    def _leg(index: int) -> Optional[str]:
        if 0 <= index < len(leg_polylines):
            return leg_polylines[index]
        return None

    if full_recompute:
        route_solution.start_leg_polyline = _leg(0)

    if full_recompute:
        for index, stop in enumerate(affected_stops):
            stop.to_next_polyline = _leg(index + 1) if index + 1 < len(affected_stops) else None
            changed.append(stop)

        route_solution.end_leg_polyline = _leg(len(affected_stops))
        return changed

    if anchor_stop is None:
        return changed

    if not affected_stops:
        anchor_stop.to_next_polyline = None
        route_solution.end_leg_polyline = _leg(0)
        changed.append(anchor_stop)
        return changed

    anchor_stop.to_next_polyline = _leg(0)
    changed.append(anchor_stop)

    for index, stop in enumerate(affected_stops):
        stop.to_next_polyline = _leg(index + 1) if index + 1 < len(affected_stops) else None
        changed.append(stop)

    route_solution.end_leg_polyline = _leg(len(affected_stops))
    return changed


def _dedupe_stops(stops: list[RouteSolutionStop]) -> list[RouteSolutionStop]:
    deduped: list[RouteSolutionStop] = []
    seen: set[int] = set()
    for stop in stops:
        stop_id = getattr(stop, "id", None)
        if stop_id in seen:
            continue
        if stop_id is not None:
            seen.add(stop_id)
        deduped.append(stop)
    return deduped


def _resolve_allowed_end(route_solution: RouteSolution) -> Optional[datetime]:
    if not route_solution.local_delivery_plan:
        return None
    delivery_plan = route_solution.local_delivery_plan.delivery_plan
    if not delivery_plan or not delivery_plan.end_date:
        return None

    end_date = delivery_plan.end_date
    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)

    if route_solution.set_end_time:
        parsed = _parse_time_string(route_solution.set_end_time)
        if parsed:
            return datetime.combine(end_date.date(), parsed, tzinfo=end_date.tzinfo)

    return datetime.combine(
        end_date.date(),
        time_cls(23, 59, 59),
        tzinfo=end_date.tzinfo,
    )


def _build_stop_warnings(
    order: Optional[Order],
    arrival_time: Optional[datetime],
    route_solution: RouteSolution,
) -> List[dict]:
    return build_stop_time_warnings(order, arrival_time, route_solution)
