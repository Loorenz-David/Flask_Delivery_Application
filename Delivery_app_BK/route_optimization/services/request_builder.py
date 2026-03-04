from __future__ import annotations

from datetime import datetime, time as time_cls, timezone, timedelta
from typing import Any, Dict, List, Optional

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.route_optimization.domain.models import (
    OptimizationContext,
    OptimizationRequest,
    Shipment,
    TimeWindow,
)
from Delivery_app_BK.route_optimization.constants.route_end_strategy import ROUND_TRIP,  LAST_STOP

DEFAULT_ROUTE_MODIFIERS = {
    "avoid_tolls": False,
    "avoid_highways": False,
    "avoid_ferries": False,
    "avoid_indoor": False,
}

DEFAULT_OBJECTIVES: List[Dict[str, Any]] = []

DEFAULT_VEHICLE_VALUES = {
    "cost_per_kilometer": 1.0,
    "travel_mode": "DRIVING",
}


def build_request(context: OptimizationContext) -> OptimizationRequest:
    incoming_data = context.incoming_data

    start_location = (
        incoming_data.get("start_location")
        or context.route_solution.start_location
        or _infer_location_from_orders(
            context.orders,
            context.route_solution.stops,
            prefer="lowest",
        )
    )

    if context.route_end_strategy == ROUND_TRIP:
        end_location = start_location
    elif context.route_end_strategy == LAST_STOP:
        end_location = _infer_location_from_orders(
            context.orders,
            context.route_solution.stops,
            prefer="highest",
        )
    else:
        end_location = (
            incoming_data.get("end_location")
            or context.route_solution.end_location
            or start_location
        )

    

    _ensure_address_format(start_location, "start_location")
    _ensure_address_format(end_location, "end_location")

    start_coordinates = _coordinates_from_location(start_location)
    end_coordinates = _coordinates_from_location(end_location)
    if not start_coordinates or not end_coordinates:
        raise ValidationFailed("Start or end location is missing coordinates.")

    shipments = _build_shipments(context)


    global_start_time, global_end_time = _resolve_global_time_bounds(
        context,
        incoming_data,
    )

    route_modifiers = dict(DEFAULT_ROUTE_MODIFIERS)
    if isinstance(incoming_data.get("route_modifiers"), dict):
        for key, value in incoming_data["route_modifiers"].items():
            if key in route_modifiers:
                route_modifiers[key] = bool(value)

    objectives = _coerce_objectives(incoming_data.get("objectives"))

    vehicle_config = incoming_data.get("vehicle", {})
    travel_mode = vehicle_config.get("travel_mode", DEFAULT_VEHICLE_VALUES["travel_mode"])
    cost_per_kilometer = vehicle_config.get(
        "cost_per_kilometer", DEFAULT_VEHICLE_VALUES["cost_per_kilometer"]
    )

    return OptimizationRequest(
        delivery_plan_id=context.delivery_plan.id,
        local_delivery_plan_id=context.local_delivery_plan.id,
        route_solution_id=context.route_solution.id,
        shipments=shipments,
        start_location=start_location,
        end_location=end_location,
        start_coordinates=start_coordinates,
        end_coordinates=end_coordinates,
        global_start_time=global_start_time,
        global_end_time=global_end_time,
        consider_traffic=bool(incoming_data.get("consider_traffic")),
        route_modifiers=route_modifiers,
        objectives=objectives,
        travel_mode=travel_mode,
        cost_per_kilometer=float(cost_per_kilometer),
        populate_transition_polylines=bool(
            incoming_data.get("populate_transition_polylines", True)
        ),
        injected_routes=_build_injected_routes(context, incoming_data),
        interpret_injected_solutions_using_labels=context.interpret_injected_solutions_using_labels,
    )


def _build_shipments(context: OptimizationContext) -> List[Shipment]:
    service_durations = _parse_service_durations(context.incoming_data)
    shipments: List[Shipment] = []

    for order in context.orders:
        coords = _coordinates_from_location(order.client_address)
        if not coords:
            raise ValidationFailed(f"Order {order.id} is missing coordinates.")
       
        time_windows = _build_time_windows(order, context)
       
        shipments.append(
            Shipment(
                order_id=order.id,
                location=coords,
                time_windows=time_windows,
                service_duration_seconds=service_durations.get(order.id),
            )
        )

    return shipments


def _build_time_windows(order, context: OptimizationContext) -> List[TimeWindow]:
    delivery_windows = _build_delivery_windows_from_order(order)
    if delivery_windows:
        return delivery_windows

    windows: List[TimeWindow] = []

    earliest = _coerce_datetime(order.earliest_delivery_date)
    latest = _coerce_datetime(order.latest_delivery_date)
    preferred_start = _parse_time_string(order.preferred_time_start)
    preferred_end = _parse_time_string(order.preferred_time_end)


    if earliest or latest:
        windows = _build_date_range_windows(
            earliest=earliest,
            latest=latest,
            preferred_start=preferred_start,
            preferred_end=preferred_end,
            context=context,
        )
        return windows
    
    if preferred_start or preferred_end:
        windows = _build_date_range_windows(
            earliest=_coerce_datetime(context.delivery_plan.start_date ),
            latest=_coerce_datetime(context.delivery_plan.end_date),
            preferred_start=preferred_start,
            preferred_end=preferred_end,
            context=context,
        )

    return windows


def _build_delivery_windows_from_order(order) -> List[TimeWindow]:
    rows = list(getattr(order, "delivery_windows", None) or [])
    if not rows:
        return []

    if len(rows) > 14:
        raise ValidationFailed(f"Order {order.id} exceeds max delivery windows (14).")

    sorted_rows = sorted(
        rows,
        key=lambda row: (
            _coerce_datetime(getattr(row, "start_at", None)) or datetime.min.replace(tzinfo=timezone.utc),
            _coerce_datetime(getattr(row, "end_at", None)) or datetime.min.replace(tzinfo=timezone.utc),
        ),
    )

    windows: List[TimeWindow] = []
    previous_end: Optional[datetime] = None
    for index, row in enumerate(sorted_rows):
        start = _coerce_datetime(getattr(row, "start_at", None))
        end = _coerce_datetime(getattr(row, "end_at", None))
        if not start or not end:
            raise ValidationFailed(
                f"Order {order.id} has invalid delivery window at index {index}.",
            )
        if end <= start:
            raise ValidationFailed(
                f"Order {order.id} has delivery window with end_at <= start_at at index {index}.",
            )
        if previous_end and start < previous_end:
            raise ValidationFailed(
                f"Order {order.id} has overlapping delivery windows.",
            )
        windows.append(TimeWindow(start_time=start, end_time=end))
        previous_end = end

    return windows


def _build_injected_routes(
    context: OptimizationContext,
    incoming_data: Dict[str, Any],
) -> Optional[List[Dict[str, Any]]]:
    incoming_routes = incoming_data.get("injected_routes")
    if incoming_routes is not None:
        return incoming_routes

    if not context.interpret_injected_solutions_using_labels:
        return None

    route_solution = context.route_solution
    stops = list(route_solution.stops or [])
    if not stops:
        return None

    eligible_stops = [
        stop for stop in stops if stop.order_id and stop.eta_status != "stale"
    ]
    if not eligible_stops:
        return None

    eligible_stops.sort(key=lambda stop: stop.stop_order or 0)

    visits = [
        {"shipment_label": f"{stop.order_id}-{route_solution.id}"}
        for stop in eligible_stops
    ]

    return [
        {
            "vehicle_label": f"vehicle-{context.local_delivery_plan.id}",
            "visits": visits,
        }
    ]


def _build_date_range_windows(
    *,
    earliest: Optional[datetime],
    latest: Optional[datetime],
    preferred_start: Optional[time_cls],
    preferred_end: Optional[time_cls],
    context: OptimizationContext,
) -> List[TimeWindow]:
    max_windows = 14
    windows: List[TimeWindow] = []

    # ---- Resolve global bounds ----
    global_start, global_end = _resolve_global_time_bounds(
        context,
        context.incoming_data,
    )

    tz = _resolve_tz(global_start, global_end)

 
    # ---- Resolve date range ----
    range_start = earliest or _coerce_datetime(context.delivery_plan.start_date)
    range_end = latest or (range_start + timedelta(days=max_windows - 1))

    tz = range_start.tzinfo


    if global_start:
        global_start = global_start.astimezone(tz)
    if global_end:
        global_end = global_end.astimezone(tz)


    if range_start.tzinfo is None:
        range_start = range_start.replace(tzinfo=tz)
    else:
        range_start = range_start.astimezone(tz)

    if range_end.tzinfo is None:
        range_end = range_end.replace(tzinfo=tz)
    else:
        range_end = range_end.astimezone(tz)


    # Clamp date range to global bounds
    if global_start and (range_start < global_start or range_start > global_end):
        range_start = global_start
    if global_end and (range_end > global_end or range_end < global_start):
        range_end = global_end


   

    # ---- Iterate day by day ----
    current_day = range_start.date()
    last_day = range_end.date()

    while current_day <= last_day and len(windows) < max_windows:
        # default full-day
        day_start = time_cls(0, 0, 0)
        day_end   = time_cls(23, 59, 49)

        # first day → respect global_start
        if global_start and current_day == global_start.date():
            day_start = global_start.timetz().replace(tzinfo=None)

        # last day → respect global_end
        if global_end and current_day == global_end.date():
            day_end = global_end.timetz().replace(tzinfo=None)

        # preferred time overrides (if present)
        if preferred_start:
            day_start = max(day_start, preferred_start)
        if preferred_end:
            day_end = min(day_end, preferred_end)
       
        start_dt = datetime.combine(current_day, day_start, tzinfo=tz)
        end_dt   = datetime.combine(current_day, day_end,   tzinfo=tz)

        if end_dt >= start_dt:
            
            windows.append(TimeWindow(start_time=start_dt, end_time=end_dt))

        current_day += timedelta(days=1)

    return windows



def _coerce_objectives(value: Any) -> List[Dict[str, Any]]:
    if isinstance(value, list) and value:
        return value
    if isinstance(value, dict):
        return [value]
    return list(DEFAULT_OBJECTIVES)


def _coordinates_from_location(location: Optional[Dict[str, Any]]) -> Optional[Dict[str, float]]:
    if not location:
        return None
    candidate = location.get("coordinates", location)
    if not isinstance(candidate, dict):
        return None
    lat = candidate.get("lat") or candidate.get("latitude")
    lng = candidate.get("lng") or candidate.get("longitude")
    if lat is None or lng is None:
        return None
    try:
        return {"latitude": float(lat), "longitude": float(lng)}
    except (TypeError, ValueError):
        return None


def _infer_location_from_orders(orders, stops=None, prefer: str = "lowest") -> Dict[str, Any]:
    if stops:
        target_stop = _select_stop_by_order(stops, prefer)
        if target_stop:
            order_lookup = {
                order.id: order for order in orders if getattr(order, "id", None) is not None
            }
            target_order = order_lookup.get(target_stop.order_id)
            if target_order and target_order.client_address:
                return target_order.client_address

    first = next((order for order in orders if order.client_address), None)
    if not first:
        raise ValidationFailed("Orders are missing client addresses for routing.")
    return first.client_address


def _select_stop_by_order(stops, prefer: str):
    eligible = [stop for stop in stops if stop.stop_order is not None]
    if not eligible:
        return None
    if prefer == "highest":
        return max(eligible, key=lambda stop: stop.stop_order)
    return min(eligible, key=lambda stop: stop.stop_order)


def _parse_service_durations(incoming_data: Dict[str, Any]) -> Dict[int, int]:
    raw = incoming_data.get("service_durations") or {}
    if not isinstance(raw, dict):
        return {}
    durations: Dict[int, int] = {}
    for key, value in raw.items():
        try:
            order_id = int(key)
        except (TypeError, ValueError):
            continue
        seconds = _parse_duration_seconds(value)
        if seconds is not None:
            durations[order_id] = seconds
    return durations


def _parse_duration_seconds(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    parsed = str(value).strip().lower()
    if not parsed:
        return None

    suffix_map = {
        "s": 1,
        "sec": 1,
        "secs": 1,
        "second": 1,
        "seconds": 1,
        "m": 60,
        "min": 60,
        "mins": 60,
        "minute": 60,
        "minutes": 60,
        "h": 3600,
        "hr": 3600,
        "hrs": 3600,
        "hour": 3600,
        "hours": 3600,
    }
    for suffix, multiplier in suffix_map.items():
        if parsed.endswith(suffix):
            numeric = parsed[: -len(suffix)].strip()
            try:
                return int(float(numeric) * multiplier)
            except ValueError:
                return None

    if ":" in parsed:
        try:
            parts = [int(part) for part in parsed.split(":")]
            while len(parts) < 3:
                parts.append(0)
            hours, minutes, seconds = parts[:3]
            return hours * 3600 + minutes * 60 + seconds
        except ValueError:
            return None

    try:
        return int(float(parsed))
    except ValueError:
        return None


def _parse_time_string(value: Optional[str]) -> Optional[time_cls]:
    if not value:
        return None
    parsed = str(value).strip()
    if not parsed:
        return None
    parts = parsed.split(":")
    try:
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0
        second = int(parts[2]) if len(parts) > 2 else 0
        return time_cls(hour=hour, minute=minute, second=second)
    except ValueError:
        return None


def _combine_date_time(base: datetime, time_value: Optional[time_cls]) -> Optional[datetime]:
    if not time_value:
        return None
    if base.tzinfo is None:
        base = base.replace(tzinfo=timezone.utc)
    return datetime.combine(base.date(), time_value, tzinfo=base.tzinfo)

def _resolve_global_time_bounds(
    context: OptimizationContext,
    incoming_data: Dict[str, Any],
) -> tuple[Optional[datetime], Optional[datetime]]:
    global_start = _coerce_datetime(incoming_data.get("global_start_time"))
    global_end = _coerce_datetime(incoming_data.get("global_end_time"))

    if global_start is None:
        global_start = _merge_plan_date_with_route_time(
            context.delivery_plan.start_date,
            context.route_solution.set_start_time,
            use_now_if_today=True,
        )

    if global_end is None:
        global_end = _merge_plan_date_with_route_time(
            context.delivery_plan.end_date,
            context.route_solution.set_end_time,
            use_now_if_today=False,
        )

    return global_start, global_end


def _merge_plan_date_with_route_time(
    plan_date_value: Any,
    time_value: Optional[str],
    *,
    use_now_if_today: bool,
) -> Optional[datetime]:
    base_date = _coerce_datetime(plan_date_value)
    if not base_date:
        return None

    parsed_time = _parse_time_string(time_value)
    if parsed_time:
        return _combine_date_time(base_date, parsed_time) or base_date

    if use_now_if_today:
        now = datetime.now(tz=base_date.tzinfo or timezone.utc)
        if base_date.date() == now.date():
            return now

    return base_date


def _coerce_datetime(value: Any, tz = timezone.utc) -> Optional[datetime]:
    if not value:
        return None
   
    if isinstance(value, datetime):
        return value.astimezone(tz) if value.tzinfo else value.replace(tzinfo=tz)

    try:
        parsed = datetime.fromisoformat(str(value))
    except ValueError:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=tz)   

    return parsed

def _ensure_address_format(location: Dict[str, Any], label: str) -> None:
    if not isinstance(location, dict):
        raise ValidationFailed(f"{label} must be a JSON object.")
    if not location.get("street_address") or not location.get("country"):
        raise ValidationFailed(f"{label} must include street_address and country.")
    coordinates = location.get("coordinates")
    if not isinstance(coordinates, dict):
        raise ValidationFailed(f"{label} must include coordinates.")
    if coordinates.get("lat") is None or coordinates.get("lng") is None:
        raise ValidationFailed(f"{label} coordinates must include lat and lng.")

def _resolve_tz(*datetimes: Optional[datetime]) -> timezone:
    for dt in datetimes:
        if isinstance(dt, datetime) and dt.tzinfo is not None:
            return dt.tzinfo
    return timezone.utc
