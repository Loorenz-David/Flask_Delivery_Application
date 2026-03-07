from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, time as time_cls, timezone
from typing import List, Tuple

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import (
    DeliveryPlan,
    InternationalShippingPlan,
    LocalDeliveryPlan,
    RouteSolution,
    StorePickupPlan,
)
from Delivery_app_BK.route_optimization.constants.is_optimized import (
    IS_OPTIMIZED_NOT_OPTIMIZED,
)
from Delivery_app_BK.route_optimization.constants.route_end_strategy import (
    CUSTOM_END_ADDRESS,
    LAST_STOP,
    ROUND_TRIP,
)
from Delivery_app_BK.services.commands.utils import generate_client_id
from Delivery_app_BK.services.domain.local_delivery import normalize_service_time_payload

from ...context import ServiceContext
from ..base.create_instance import create_instance


PlanTypeFactory = Callable[[ServiceContext, DeliveryPlan, dict], Tuple[object, List[object]]]


PLAN_TYPE_MODEL_MAP = {
    "local_delivery": LocalDeliveryPlan,
    "international_shipping": InternationalShippingPlan,
    "store_pickup": StorePickupPlan,
}


def _resolve_client_id(client_id: str | None, prefix: str) -> str:
    if isinstance(client_id, str):
        normalized = client_id.strip()
        if normalized:
            return normalized
    return generate_client_id(prefix)


def _build_local_delivery_plan_type(
    ctx: ServiceContext,
    plan_instance: DeliveryPlan,
    defaults: dict,
) -> Tuple[LocalDeliveryPlan, List[object]]:
    client_id = defaults.get("client_id") if isinstance(defaults, dict) else None
    local_delivery_client_id = _resolve_client_id(client_id, "local_delivery")
    plan_type_instance = create_instance(
        ctx,
        LocalDeliveryPlan,
        {"client_id": local_delivery_client_id},
    )

    route_solution_defaults = _normalize_local_delivery_route_solution_defaults(
        ctx,
        plan_instance,
        defaults,
    )
    route_solution = RouteSolution(
        client_id=generate_client_id("route_solution"),
        label="variant 1",
        is_selected=True,
        is_optimized=IS_OPTIMIZED_NOT_OPTIMIZED,
        stop_count=0,
        team_id=ctx.team_id,
        start_location=route_solution_defaults["start_location"],
        end_location=route_solution_defaults["end_location"],
        set_start_time=route_solution_defaults["set_start_time"],
        expected_start_time=route_solution_defaults["expected_start_time"],
        set_end_time=route_solution_defaults["set_end_time"],
        stops_service_time=route_solution_defaults["stops_service_time"],
        route_end_strategy=route_solution_defaults["route_end_strategy"],
        driver_id=route_solution_defaults["driver_id"],
    )
    plan_type_instance.route_solutions.append(route_solution)
    return plan_type_instance, [route_solution]


def _build_simple_plan_type(
    ctx: ServiceContext,
    plan_instance: DeliveryPlan,
    defaults: dict,
    plan_type_model,
    client_id_prefix: str,
) -> Tuple[object, List[object]]:
    client_id = defaults.get("client_id") if isinstance(defaults, dict) else None
    plan_type_instance = create_instance(
        ctx,
        plan_type_model,
        {"client_id": _resolve_client_id(client_id, client_id_prefix)},
    )
    return plan_type_instance, []


PLAN_TYPE_FACTORIES: dict[str, PlanTypeFactory] = {
    "local_delivery": _build_local_delivery_plan_type,
    "international_shipping": lambda ctx, plan_instance, defaults: _build_simple_plan_type(
        ctx,
        plan_instance,
        defaults,
        InternationalShippingPlan,
        "international_shipping",
    ),
    "store_pickup": lambda ctx, plan_instance, defaults: _build_simple_plan_type(
        ctx,
        plan_instance,
        defaults,
        StorePickupPlan,
        "store_pickup",
    ),
}


def build_plan_type_instances(
    ctx: ServiceContext,
    plan_type: str,
    plan_instance: DeliveryPlan,
    plan_type_defaults: dict | None = None,
) -> Tuple[object, List[object]]:
    if not plan_type:
        raise ValidationFailed("Missing plan_type.")
    if plan_type not in PLAN_TYPE_MODEL_MAP:
        raise ValidationFailed(f"Invalid plan_type: {plan_type}")

    factory = PLAN_TYPE_FACTORIES.get(plan_type)
    if not factory:
        raise ValidationFailed(f"No builder registered for plan_type: {plan_type}")

    defaults = plan_type_defaults if isinstance(plan_type_defaults, dict) else {}
    plan_type_instance, extra_instances = factory(ctx, plan_instance, defaults)
    setattr(plan_instance, plan_type, plan_type_instance)
    return plan_type_instance, extra_instances


def _normalize_local_delivery_route_solution_defaults(
    ctx: ServiceContext,
    plan_instance: DeliveryPlan,
    defaults: dict,
) -> dict:
    route_solution_defaults = defaults.get("route_solution")
    if not isinstance(route_solution_defaults, dict):
        route_solution_defaults = {}

    raw_strategy = route_solution_defaults.get("route_end_strategy")
    allowed_strategies = {ROUND_TRIP, CUSTOM_END_ADDRESS, LAST_STOP}
    route_end_strategy = (
        raw_strategy if isinstance(raw_strategy, str) and raw_strategy in allowed_strategies else ROUND_TRIP
    )

    raw_start_location = route_solution_defaults.get("start_location")
    start_location = raw_start_location if isinstance(raw_start_location, dict) else None

    raw_end_location = route_solution_defaults.get("end_location")
    end_location = raw_end_location if isinstance(raw_end_location, dict) else None

    raw_start_time = route_solution_defaults.get("set_start_time")
    set_start_time = raw_start_time if isinstance(raw_start_time, str) else None
    expected_start_time = _build_expected_start_time(
        plan_start=plan_instance.start_date,
        set_start_time=set_start_time,
    )

    raw_end_time = route_solution_defaults.get("set_end_time")
    set_end_time = raw_end_time if isinstance(raw_end_time, str) else None

    raw_driver_id = route_solution_defaults.get("driver_id")
    driver_id = raw_driver_id if isinstance(raw_driver_id, int) and not isinstance(raw_driver_id, bool) else None
    stops_service_time = normalize_service_time_payload(
        route_solution_defaults.get("stops_service_time")
    )

    return {
        "start_location": start_location,
        "end_location": end_location,
        "set_start_time": set_start_time,
        "expected_start_time": expected_start_time,
        "set_end_time": set_end_time,
        "stops_service_time": stops_service_time,
        "route_end_strategy": route_end_strategy,
        "driver_id": driver_id,
    }


def _parse_hhmm(value: str | None) -> time_cls | None:
    if not isinstance(value, str):
        return None

    parsed = value.strip()
    if not parsed:
        return None

    parts = parsed.split(":")
    if len(parts) not in (2, 3):
        return None

    try:
        hour = int(parts[0])
        minute = int(parts[1])
        second = int(parts[2]) if len(parts) == 3 else 0
        return time_cls(hour=hour, minute=minute, second=second)
    except (TypeError, ValueError):
        return None


def _ensure_utc_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _build_expected_start_time(
    plan_start: datetime | None,
    set_start_time: str | None,
) -> datetime | None:
    normalized_start = _ensure_utc_datetime(plan_start)
    parsed_time = _parse_hhmm(set_start_time)

    if not normalized_start or not parsed_time:
        return None

    # Store the exact HH:mm user-set clock time on the plan UTC date,
    # without timezone conversion.
    combined_start = datetime(
        year=normalized_start.year,
        month=normalized_start.month,
        day=normalized_start.day,
        hour=parsed_time.hour,
        minute=parsed_time.minute,
        second=parsed_time.second,
        tzinfo=timezone.utc,
    )
    return combined_start
