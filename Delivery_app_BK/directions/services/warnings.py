from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional, Tuple

from Delivery_app_BK.models import Order, RouteSolution
from Delivery_app_BK.models.mixins.validation_mixins.time_warning_validation import (
    TimeWarningFactory,
)

from Delivery_app_BK.directions.services.request_builder import build_time_windows


def ensure_utc(value: Optional[datetime]) -> Optional[datetime]:
    if not value:
        return None
    return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)


def build_stop_time_warnings(
    order: Optional[Order],
    arrival_time: Optional[datetime],
    route_solution: RouteSolution,
) -> List[dict]:
    if not order or not arrival_time:
        return []

    arrival_time = ensure_utc(arrival_time)
    windows = _build_effective_windows(order, route_solution)
    if not windows:
        return []

    for window_start, window_end in windows:
        window_start = ensure_utc(window_start)
        window_end = ensure_utc(window_end)
        if window_start and window_end and arrival_time and window_start <= arrival_time <= window_end:
            return []

    window_start, window_end = windows[0]
    window_start = ensure_utc(window_start)
    window_end = ensure_utc(window_end)
    return [
        TimeWarningFactory.time_window_violation(
            expected_time=arrival_time,
            window_start=window_start,
            window_end=window_end,
        )
    ]


def _build_effective_windows(
    order: Order,
    route_solution: RouteSolution,
) -> List[Tuple[datetime, datetime]]:
    base_date = None
    base_end_date = None
    if route_solution.local_delivery_plan and route_solution.local_delivery_plan.delivery_plan:
        plan = route_solution.local_delivery_plan.delivery_plan
        base_date = plan.start_date
        base_end_date = plan.end_date

    order_windows = build_time_windows(order, base_date, base_end_date)
    if order_windows:
        return order_windows

    fallback_start = ensure_utc(base_date)
    fallback_end = ensure_utc(base_end_date)
    if not fallback_start or not fallback_end:
        return []

    return [(fallback_start, fallback_end)]
