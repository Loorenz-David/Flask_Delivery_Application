from datetime import datetime

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import (
    DeliveryPlan,
    InternationalShippingPlan,
    LocalDeliveryPlan,
    RouteSolution,
    StorePickupPlan,
)
from Delivery_app_BK.services.queries.utils import calculate_plan_metrics


def _to_iso(value: datetime | None) -> str | None:
    if not value:
        return None
    return value.isoformat()


def serialize_created_delivery_plan(instance: DeliveryPlan) -> dict:
    serialized = {
        "id": instance.id,
        "client_id": instance.client_id,
        "label": instance.label,
        "plan_type": instance.plan_type,
        "start_date": _to_iso(instance.start_date),
        "end_date": _to_iso(instance.end_date),
        "created_at": _to_iso(instance.created_at),
        "state_id": instance.state_id,
    }
    serialized.update(calculate_plan_metrics(instance))
    return serialized


def _serialize_local_delivery_plan(instance: LocalDeliveryPlan) -> dict:
    return {
        "id": instance.id,
        "client_id": instance.client_id,
        "actual_start_time": _to_iso(instance.actual_start_time),
        "actual_end_time": _to_iso(instance.actual_end_time),
        "driver_id": instance.driver_id,
        "delivery_plan_id": instance.delivery_plan_id,
    }


def _serialize_international_shipping_plan(instance: InternationalShippingPlan) -> dict:
    return {
        "id": instance.id,
        "client_id": instance.client_id,
        "carrier_name": instance.carrier_name,
        "delivery_plan_id": instance.delivery_plan_id,
    }


def _serialize_store_pickup_plan(instance: StorePickupPlan) -> dict:
    return {
        "id": instance.id,
        "client_id": instance.client_id,
        "pickup_location": instance.pickup_location,
        "assigned_user_id": instance.assigned_user_id,
        "delivery_plan_id": instance.delivery_plan_id,
    }


def serialize_created_delivery_plan_type(plan_type: str, instance) -> dict:
    if plan_type == "local_delivery":
        return _serialize_local_delivery_plan(instance)
    if plan_type == "international_shipping":
        return _serialize_international_shipping_plan(instance)
    if plan_type == "store_pickup":
        return _serialize_store_pickup_plan(instance)
    raise ValidationFailed(f"Unsupported plan_type serializer for '{plan_type}'.")


def serialize_created_route_solution(instance: RouteSolution) -> dict:
    return {
        "id": instance.id,
        "client_id": instance.client_id,
        "_representation": "full",
        "label": instance.label,
        "version": instance.version,
        "algorithm": instance.algorithm,
        "score": instance.score,
        "total_distance_meters": instance.total_distance_meters,
        "total_travel_time_seconds": instance.total_travel_time_seconds,
        "start_leg_polyline": instance.start_leg_polyline,
        "end_leg_polyline": instance.end_leg_polyline,
        "has_route_warnings": instance.has_route_warnings,
        "route_warnings": instance.route_warnings,
        "start_location": instance.start_location,
        "end_location": instance.end_location,
        "expected_start_time": _to_iso(instance.expected_start_time),
        "expected_end_time": _to_iso(instance.expected_end_time),
        "set_start_time": instance.set_start_time,
        "set_end_time": instance.set_end_time,
        "stops_service_time": instance.stops_service_time,
        "is_selected": instance.is_selected,
        "is_optimized": instance.is_optimized,
        "driver_id": instance.driver_id,
        "route_end_strategy": instance.route_end_strategy,
        "local_delivery_plan_id": instance.local_delivery_plan_id,
        "created_at": _to_iso(instance.created_at),
    }
