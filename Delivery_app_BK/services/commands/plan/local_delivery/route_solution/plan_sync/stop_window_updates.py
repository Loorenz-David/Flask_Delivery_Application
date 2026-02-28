from datetime import datetime
from typing import Tuple

from Delivery_app_BK.models import RouteSolution
from Delivery_app_BK.models.mixins.validation_mixins.time_warning_validation import (
    TimeWarningFactory,
)
from Delivery_app_BK.route_optimization.constants.skip_reasons import (
    OUTSIDE_TIME_WINDOW,
)

from .normalizers import ensure_utc, normalize_skip_reason


def apply_time_window_update(
    route_solution: RouteSolution,
    old_window: Tuple[datetime, datetime],
    new_window: Tuple[datetime, datetime],
    shift_times: bool,
) -> Tuple[bool, bool]:
    old_start, _ = old_window
    new_start, new_end = new_window
    old_start = ensure_utc(old_start)
    new_start = ensure_utc(new_start)
    new_end = ensure_utc(new_end)
  
    shift_delta = None
    if shift_times and new_start and old_start and new_start != old_start:
        shift_delta = new_start - old_start
   
    has_updates = False
    has_violation = False

    for stop in route_solution.stops or []:
        arrival = ensure_utc(stop.expected_arrival_time)
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
            stop.reason_was_skipped = normalize_skip_reason(OUTSIDE_TIME_WINDOW)
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
            if stop.reason_was_skipped == normalize_skip_reason(OUTSIDE_TIME_WINDOW):
                stop.reason_was_skipped = None
                has_updates = True

    return has_updates, has_violation
