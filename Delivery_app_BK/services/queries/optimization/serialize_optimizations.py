from typing import Type
from flask_sqlalchemy.model import Model

from ...context import ServiceContext
from ..utils import map_return_values


def serialize_optimizations(instances: Type[Model], ctx: ServiceContext):
    unpacked_instances = []

    for instance in instances:
        created_at = instance.created_at
        stops_by_order = {}

        for stop in (instance.stops or []):
            stops_by_order[stop.order_id] = {
                "id": stop.id,
                "client_id": stop.client_id,
                "route_solution_id": stop.route_solution_id,
                "order_id": stop.order_id,
                "waiting_time": stop.waiting_time,
                "in_range": stop.in_range,
                "stop_order": stop.stop_order,
                "delivery_after": stop.delivery_after,
                "delivery_before": stop.delivery_before,
                "expected_arrival_time": _serialize_datetime(stop.expected_arrival_time),
                "actual_arrival_time": stop.actual_arrival_time,
                "team_id": stop.team_id,
            }

        unpacked = {
            "id": instance.id,
            "client_id": instance.client_id,
            "version": instance.version,
            "algorithm": instance.algorithm,
            "score": instance.score,
            "created_at": created_at.isoformat() if created_at else None,
            "is_selected": instance.is_selected,
            "local_delivery_plan_id": instance.local_delivery_plan_id,
            "team_id": instance.team_id,
            "stops": stops_by_order,
        }
        unpacked_instances.append(unpacked)

    return map_return_values(unpacked_instances, ctx, "route_solution")


def _serialize_datetime(value):
    if not value:
        return None
    return value.isoformat()
