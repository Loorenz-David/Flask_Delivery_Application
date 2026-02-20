from __future__ import annotations

from datetime import datetime, time as time_cls, timezone
from typing import Dict, List, Optional

from Delivery_app_BK.models import Order, RouteSolution, RouteSolutionStop
from Delivery_app_BK.models.mixins.validation_mixins.time_warning_validation import (
    TimeWarningFactory,
)

from Delivery_app_BK.directions.domain.models import DirectionsResult
from Delivery_app_BK.directions.services.request_builder import (
    build_time_windows,
    _parse_time_string,
)


def _ensure_utc(value: Optional[datetime]) -> Optional[datetime]:
    if not value:
        return None
    return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)


def apply_directions_result(
    route_solution: RouteSolution,
    directions_result: DirectionsResult,
    orders_by_id: Dict[int, Order],
) -> None:
    route_solution.total_distance_meters = directions_result.total_distance_meters
    route_solution.total_travel_time_seconds = directions_result.total_duration_seconds
    route_solution.route_polyline = directions_result.polyline
    if directions_result.start_time is not None:
        route_solution.expected_start_time = _ensure_utc(directions_result.start_time)
    if directions_result.end_time is not None:
        route_solution.expected_end_time = _ensure_utc(directions_result.end_time)

    route_warnings: List[dict] = []

    allowed_end = _ensure_utc(_resolve_allowed_end(route_solution))
    end_time = _ensure_utc(directions_result.end_time)
    
    if allowed_end and end_time:
        if end_time > allowed_end:
            route_warnings.append(
                TimeWarningFactory.route_end_time_exceeded(
                    expected_end=end_time,
                    allowed_end=allowed_end,
                )
            )

    route_solution.route_warnings = route_warnings or None
    route_solution.has_route_warnings = bool(route_warnings)

    for stop_result in directions_result.stop_results:
        stop = _find_stop(route_solution, stop_result.order_id)
        if not stop:
            continue
        stop.expected_arrival_time = _ensure_utc(stop_result.arrival_time)
        stop.eta_status = "estimated"

        warnings = _build_stop_warnings(
            orders_by_id.get(stop_result.order_id),
            stop.expected_arrival_time,
            route_solution,
        )

        stop.constraint_warnings = warnings or None
        stop.has_constraint_violation = bool(warnings)


def _find_stop(route_solution: RouteSolution, order_id: int) -> Optional[RouteSolutionStop]:
    for stop in route_solution.stops or []:
        if stop.order_id == order_id:
            return stop
    return None


def _build_stop_warnings(
    order: Optional[Order],
    arrival_time: Optional[datetime],
    route_solution: RouteSolution,
) -> List[dict]:
    if not order or not arrival_time:
        return []

    base_date = None
    base_end_date = None
    if route_solution.local_delivery_plan and route_solution.local_delivery_plan.delivery_plan:
        plan = route_solution.local_delivery_plan.delivery_plan
        base_date = plan.start_date
        base_end_date = plan.end_date

    arrival_time = _ensure_utc(arrival_time)
    windows = build_time_windows(order, base_date, base_end_date)

    
    if not windows:
        return []
    
    for window_start, window_end in windows:
        window_start = _ensure_utc(window_start)
        window_end = _ensure_utc(window_end)
        if window_start and window_end and arrival_time and window_start <= arrival_time <= window_end:
            return []
    
    window_start, window_end = windows[0]
    window_start = _ensure_utc(window_start)
    window_end = _ensure_utc(window_end)
    return [
        TimeWarningFactory.time_window_violation(
            expected_time=arrival_time,
            window_start=window_start,
            window_end=window_end,
        )
    ]


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

    # default to end of day if no explicit end time is provided
    return datetime.combine(
        end_date.date(),
        time_cls(23, 59, 59),
        tzinfo=end_date.tzinfo,
    )
