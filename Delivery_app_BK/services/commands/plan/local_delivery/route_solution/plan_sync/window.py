from datetime import datetime, time as time_cls, timezone
from typing import Optional, Tuple

from Delivery_app_BK.directions.services.request_builder import (
    _coerce_datetime,
    _combine_date_time,
    _parse_time_string,
)
from Delivery_app_BK.errors import ValidationFailed


def resolve_window(
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


def validate_window(window: Optional[Tuple[datetime, datetime]]) -> None:
    if not window:
        return
    if window[1] < window[0]:
        raise ValidationFailed("Route solution end time cannot be before start time.")
