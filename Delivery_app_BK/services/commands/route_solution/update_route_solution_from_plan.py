from __future__ import annotations

from datetime import datetime, time as time_cls, timezone
from typing import Optional, Tuple

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import RouteSolution
from Delivery_app_BK.directions import refresh_route_solution
from Delivery_app_BK.models.mixins.validation_mixins.time_warning_validation import (
    TimeWarningFactory,
)
from Delivery_app_BK.route_optimization.constants.is_optimized import (
    IS_OPTIMIZED_NOT_OPTIMIZED,
    IS_OPTIMIZED_PARTIAL,
)
from Delivery_app_BK.route_optimization.constants.route_end_strategy import ROUND_TRIP, CUSTOM_END_ADDRESS
from Delivery_app_BK.route_optimization.constants.skip_reasons import (
    OUTSIDE_TIME_WINDOW,
)
from Delivery_app_BK.directions.services.request_builder import (
    _parse_time_string,
    _coerce_datetime,
    _combine_date_time,
)

from .clone import clone_route_solution


def _ensure_utc(value: datetime | None) -> datetime | None:
    if not value:
        return None
    return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)



def update_route_solution_from_plan(
    route_solution: RouteSolution,
    updates: dict | None,
    plan_start: datetime,
    plan_end: datetime,
    previous_plan_start: datetime | None = None,
    previous_plan_end: datetime | None = None,
    create_variant_on_save: bool = False,
    time_zone:str = None
) -> Tuple[RouteSolution, bool, RouteSolution | None]:
    updates = updates or {}

    original_route_solution = None
    original_is_optimized = route_solution.is_optimized

    if create_variant_on_save:
        route_solution, _, original_route_solution = clone_route_solution(route_solution)
        if original_is_optimized == IS_OPTIMIZED_NOT_OPTIMIZED:
            route_solution.is_optimized = IS_OPTIMIZED_NOT_OPTIMIZED
            if original_route_solution is not None:
                original_route_solution.is_optimized = IS_OPTIMIZED_NOT_OPTIMIZED

    old_set_start_time = route_solution.set_start_time
    old_set_end_time = route_solution.set_end_time

    has_start_location = "start_location" in updates
    has_end_location = "end_location" in updates
    has_set_start = "set_start_time" in updates
    has_set_end = "set_end_time" in updates
    has_driver = "driver_id" in updates
    has_route_end_strategy = "route_end_strategy" in updates

    start_location = updates.get("start_location")
    end_location = updates.get("end_location")

    set_start_time = _normalize_time_value(updates.get("set_start_time"))
    set_end_time = _normalize_time_value(updates.get("set_end_time"))
    driver_id = updates.get("driver_id")
    route_end_strategy = updates.get("route_end_strategy")

    has_address_change = False
    if has_start_location and start_location != route_solution.start_location:
        route_solution.start_location = start_location
        has_address_change = True
    if has_end_location and end_location != route_solution.end_location:
        route_solution.end_location = end_location
        has_address_change = True
    if has_route_end_strategy:
        if route_end_strategy == ROUND_TRIP and start_location != end_location:
            route_solution.end_location = route_solution.start_location
            has_address_change = True
        route_solution.route_end_strategy = route_end_strategy
        

    has_time_change = False
    if has_set_start and set_start_time != route_solution.set_start_time:
        route_solution.set_start_time = set_start_time
        has_time_change = True
    if has_set_end and set_end_time != route_solution.set_end_time:
        route_solution.set_end_time = set_end_time
        has_time_change = True

    if has_driver:
        route_solution.driver_id = driver_id

    old_window = _resolve_window(
        previous_plan_start or plan_start,
        previous_plan_end or plan_end,
        old_set_start_time,
        old_set_end_time,
    )
    new_window = _resolve_window(
        plan_start,
        plan_end,
        route_solution.set_start_time,
        route_solution.set_end_time,
    )

    _validate_window(new_window)

    window_changed = old_window != new_window
    stops_changed = original_route_solution is not None
    
    if has_address_change:
        if route_solution.is_optimized != IS_OPTIMIZED_NOT_OPTIMIZED:
            route_solution.is_optimized = IS_OPTIMIZED_PARTIAL
            refresh_route_solution(route_solution, time_zone=time_zone)
            stops_changed = True

    if has_time_change and route_solution.is_optimized != IS_OPTIMIZED_NOT_OPTIMIZED:
        route_solution.is_optimized = IS_OPTIMIZED_PARTIAL

    if window_changed and new_window and old_window:
        shift_times = not has_address_change
        window_changes, has_violation = _apply_time_window_update(
            route_solution,
            old_window,
            new_window,
            shift_times=shift_times,
        )
        stops_changed = stops_changed or window_changes
        if has_violation:
            route_solution.is_optimized = IS_OPTIMIZED_PARTIAL

    return route_solution, stops_changed, original_route_solution



def _resolve_window(
    plan_start: datetime,
    plan_end: datetime,
    set_start_time: Optional[str],
    set_end_time: Optional[str],
) -> Optional[Tuple[datetime, datetime]]:
    start_date = _coerce_datetime(plan_start)
    end_date = _coerce_datetime(plan_end)
    if not start_date or not end_date:
        return None

    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)
    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)

    start_time = _parse_time_string(set_start_time) if set_start_time else None
    end_time = _parse_time_string(set_end_time) if set_end_time else None

    window_start = _combine_date_time(start_date, start_time) or datetime.combine(
        start_date.date(),
        time_cls(0, 0, 0),
        tzinfo=start_date.tzinfo,
    )
    window_end = _combine_date_time(end_date, end_time) or datetime.combine(
        end_date.date(),
        time_cls(23, 59, 59),
        tzinfo=end_date.tzinfo,
    )

    return window_start, window_end



def _validate_window(window: Optional[Tuple[datetime, datetime]]) -> None:
    if not window:
        return
    if window[1] < window[0]:
        raise ValidationFailed("Route solution end time cannot be before start time.")



def _apply_time_window_update(
    route_solution: RouteSolution,
    old_window: Tuple[datetime, datetime],
    new_window: Tuple[datetime, datetime],
    shift_times: bool,
) -> Tuple[bool, bool]:
    old_start, _ = old_window
    new_start, new_end = new_window
    old_start = _ensure_utc(old_start)
    new_start = _ensure_utc(new_start)
    new_end = _ensure_utc(new_end)

    shift_delta = None
    if shift_times and new_start and old_start and new_start > old_start:
        shift_delta = new_start - old_start

    has_updates = False
    has_violation = False

    for stop in route_solution.stops or []:
        arrival = _ensure_utc(stop.expected_arrival_time)
        if arrival:
            stop.expected_arrival_time = arrival
        if shift_delta and arrival:
            stop.expected_arrival_time = arrival + shift_delta
            stop.eta_status = "estimated"
            arrival = stop.expected_arrival_time
            has_updates = True

        violation = False
        if arrival and new_start and new_end:
            if arrival < new_start or arrival > new_end:
                violation = True

        if violation:
            stop.constraint_warnings = [
                TimeWarningFactory.time_window_violation(
                    expected_time=arrival,
                    window_start=new_start,
                    window_end=new_end,
                )
            ]
            stop.has_constraint_violation = True
            stop.reason_was_skipped = _normalize_skip_reason(OUTSIDE_TIME_WINDOW)
            stop.eta_status = "estimated"
            has_updates = True
            has_violation = True
        else:
            if stop.constraint_warnings:
                filtered = [
                    warning
                    for warning in stop.constraint_warnings
                    if warning.get("type") != "time_window_violation"
                ]
                if filtered:
                    stop.constraint_warnings = filtered
                    stop.has_constraint_violation = True
                else:
                    stop.constraint_warnings = None
                    stop.has_constraint_violation = False
                has_updates = True
            if stop.reason_was_skipped == _normalize_skip_reason(OUTSIDE_TIME_WINDOW):
                stop.reason_was_skipped = None
                has_updates = True

    return has_updates, has_violation



def _normalize_time_value(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    parsed = str(value).strip()
    if not parsed:
        return None
    return parsed


def _normalize_skip_reason(value):
    if isinstance(value, (list, tuple)):
        return value[0] if value else None
    return value
