from dataclasses import dataclass
from datetime import datetime

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.services.requests.common.datetime import (
    normalize_end_date,
    normalize_start_date,
    parse_datetime_utc,
)
from Delivery_app_BK.services.requests.common.fields import validate_unexpected
from Delivery_app_BK.services.requests.common.types import (
    parse_optional_time_zone,
    validate_str,
)


ALLOWED_TOP_LEVEL_FIELDS = {
    "local_delivery_plan_id",
    "delivery_plan",
    "local_delivery_plan",
    "route_solution",
    "create_variant_on_save",
    "time_zone",
}


@dataclass
class DeliveryPlanPatchRequest:
    label: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    has_label: bool = False
    has_start_date: bool = False
    has_end_date: bool = False


@dataclass
class LocalDeliveryPlanPatchRequest:
    driver_id: int | None = None
    actual_start_time: datetime | None = None
    actual_end_time: datetime | None = None
    has_driver_id: bool = False
    has_actual_start_time: bool = False
    has_actual_end_time: bool = False


@dataclass
class RouteSolutionPatchRequest:
    route_solution_id: int | str | None = None
    start_location: dict | None = None
    end_location: dict | None = None
    set_start_time: str | None = None
    set_end_time: str | None = None
    route_end_strategy: str | None = None
    driver_id: int | None = None
    has_start_location: bool = False
    has_end_location: bool = False
    has_set_start_time: bool = False
    has_set_end_time: bool = False
    has_route_end_strategy: bool = False
    has_driver_id: bool = False


@dataclass
class LocalDeliverySettingsRequest:
    local_delivery_plan_id: int | str
    delivery_plan: DeliveryPlanPatchRequest
    local_delivery_plan: LocalDeliveryPlanPatchRequest
    route_solution: RouteSolutionPatchRequest
    create_variant_on_save: bool
    time_zone: str | None


def parse_update_local_delivery_settings_request(raw: dict) -> LocalDeliverySettingsRequest:
    if not isinstance(raw, dict):
        raise ValidationFailed("Payload must be an object.")

    validate_unexpected(
        raw,
        ALLOWED_TOP_LEVEL_FIELDS,
        context_msg="Unexpected fields in local delivery settings payload:",
    )

    local_delivery_plan_id = _validate_identifier(
        raw.get("local_delivery_plan_id"),
        field="local_delivery_plan_id",
    )

    delivery_plan_raw = _as_dict(raw.get("delivery_plan"), field="delivery_plan")
    local_delivery_raw = _as_dict(
        raw.get("local_delivery_plan"), field="local_delivery_plan"
    )
    route_solution_raw = _as_dict(raw.get("route_solution"), field="route_solution")

    route_solution_id = (
        route_solution_raw.get("id")
        or route_solution_raw.get("route_solution_id")
    )
    route_solution_id = _validate_identifier(
        route_solution_id,
        field="route_solution id",
    )

    delivery_plan_patch = _parse_delivery_plan_patch(delivery_plan_raw)
    local_delivery_patch = _parse_local_delivery_patch(local_delivery_raw)
    route_solution_patch = _parse_route_solution_patch(
        route_solution_id=route_solution_id,
        route_solution_raw=route_solution_raw,
    )

    # Route solution driver is the source of truth for this flow.
    effective_driver_provided = (
        route_solution_patch.has_driver_id or local_delivery_patch.has_driver_id
    )
    if effective_driver_provided:
        effective_driver_id = (
            route_solution_patch.driver_id
            if route_solution_patch.has_driver_id
            else local_delivery_patch.driver_id
        )
        local_delivery_patch.driver_id = effective_driver_id
        local_delivery_patch.has_driver_id = True
        route_solution_patch.driver_id = effective_driver_id
        route_solution_patch.has_driver_id = True

    if (
        delivery_plan_patch.has_start_date
        and delivery_plan_patch.has_end_date
        and delivery_plan_patch.start_date is not None
        and delivery_plan_patch.end_date is not None
        and delivery_plan_patch.end_date < delivery_plan_patch.start_date
    ):
        raise ValidationFailed("delivery plan end date cannot be before start date.")

    time_zone = _parse_time_zone(raw.get("time_zone"))
    create_variant_on_save = bool(raw.get("create_variant_on_save"))

    return LocalDeliverySettingsRequest(
        local_delivery_plan_id=local_delivery_plan_id,
        delivery_plan=delivery_plan_patch,
        local_delivery_plan=local_delivery_patch,
        route_solution=route_solution_patch,
        create_variant_on_save=create_variant_on_save,
        time_zone=time_zone,
    )


def _parse_delivery_plan_patch(raw: dict) -> DeliveryPlanPatchRequest:
    patch = DeliveryPlanPatchRequest()

    if "label" in raw:
        patch.has_label = True
        patch.label = validate_str(raw.get("label"), field="delivery_plan.label")

    if "start_date" in raw:
        patch.has_start_date = True
        if raw.get("start_date") is not None:
            patch.start_date = normalize_start_date(raw.get("start_date"))

    if "end_date" in raw:
        patch.has_end_date = True
        if raw.get("end_date") is not None:
            patch.end_date = normalize_end_date(raw.get("end_date"))

    return patch


def _parse_local_delivery_patch(raw: dict) -> LocalDeliveryPlanPatchRequest:
    patch = LocalDeliveryPlanPatchRequest()

    if "driver_id" in raw:
        patch.has_driver_id = True
        patch.driver_id = _validate_nullable_int(
            raw.get("driver_id"),
            field="local_delivery_plan.driver_id",
        )

    if "actual_start_time" in raw:
        patch.has_actual_start_time = True
        patch.actual_start_time = _validate_nullable_datetime(
            raw.get("actual_start_time"),
            field="local_delivery_plan.actual_start_time",
        )

    if "actual_end_time" in raw:
        patch.has_actual_end_time = True
        patch.actual_end_time = _validate_nullable_datetime(
            raw.get("actual_end_time"),
            field="local_delivery_plan.actual_end_time",
        )

    return patch


def _parse_route_solution_patch(
    route_solution_id: int | str,
    route_solution_raw: dict,
) -> RouteSolutionPatchRequest:
    patch = RouteSolutionPatchRequest(route_solution_id=route_solution_id)

    if "start_location" in route_solution_raw:
        patch.has_start_location = True
        patch.start_location = _validate_nullable_location(
            route_solution_raw.get("start_location"),
            field="route_solution.start_location",
        )

    if "end_location" in route_solution_raw:
        patch.has_end_location = True
        patch.end_location = _validate_nullable_location(
            route_solution_raw.get("end_location"),
            field="route_solution.end_location",
        )

    if "set_start_time" in route_solution_raw:
        patch.has_set_start_time = True
        patch.set_start_time = _normalize_nullable_time_string(
            route_solution_raw.get("set_start_time")
        )

    if "set_end_time" in route_solution_raw:
        patch.has_set_end_time = True
        patch.set_end_time = _normalize_nullable_time_string(
            route_solution_raw.get("set_end_time")
        )

    if "route_end_strategy" in route_solution_raw:
        patch.has_route_end_strategy = True
        value = route_solution_raw.get("route_end_strategy")
        patch.route_end_strategy = (
            validate_str(value, field="route_solution.route_end_strategy")
            if value is not None
            else None
        )

    if "driver_id" in route_solution_raw:
        patch.has_driver_id = True
        patch.driver_id = _validate_nullable_int(
            route_solution_raw.get("driver_id"),
            field="route_solution.driver_id",
        )

    return patch


def _as_dict(value, *, field: str) -> dict:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValidationFailed(f"{field} must be an object.")
    return value


def _validate_identifier(value, *, field: str) -> int | str:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip()
        if normalized:
            return normalized
    raise ValidationFailed(f"{field} is required.")


def _validate_nullable_int(value, *, field: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    raise ValidationFailed(f"{field} must be an integer.")


def _validate_nullable_datetime(value, *, field: str) -> datetime | None:
    if value is None:
        return None
    parsed = parse_datetime_utc(value)
    if not parsed:
        raise ValidationFailed(f"{field} must be a valid date.")
    return parsed


def _validate_nullable_location(value, *, field: str) -> dict | None:
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    raise ValidationFailed(f"{field} must be an object.")


def _normalize_nullable_time_string(value) -> str | None:
    if value is None:
        return None
    parsed = str(value).strip()
    if not parsed:
        return None
    return parsed


def _parse_time_zone(value) -> str | None:
    return parse_optional_time_zone(value, field="time_zone")
