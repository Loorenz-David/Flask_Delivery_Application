from typing import List

from Delivery_app_BK.models import RouteSolution

from ...context import ServiceContext
from ..utils import map_return_values


def serialize_route_solution(instance: RouteSolution) -> dict:
    created_at = instance.created_at
    expected_start_time = instance.expected_start_time
    expected_end_time = instance.expected_end_time
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
        "route_polyline": instance.route_polyline,
        "has_route_warnings": instance.has_route_warnings,
        "route_warnings": instance.route_warnings,
        "start_location": instance.start_location,
        "end_location": instance.end_location,
        "expected_start_time": expected_start_time.isoformat() if expected_start_time else None,
        "expected_end_time": expected_end_time.isoformat() if expected_end_time else None,
        "set_start_time": instance.set_start_time,
        "set_end_time": instance.set_end_time,
        "is_selected": instance.is_selected,
        "is_optimized": instance.is_optimized,
        "driver_id": instance.driver_id,
        "route_end_strategy": instance.route_end_strategy,
        "local_delivery_plan_id":instance.local_delivery_plan_id,
        "created_at": created_at.isoformat() if created_at else None,
    }


def serialize_route_solution_partial(instance: RouteSolution) -> dict:
    return {
        "id": instance.id,
        "client_id": instance.client_id,
        "local_delivery_plan_id": instance.local_delivery_plan_id,
        "_representation": "partial",
        "label": instance.label,
        "score": instance.score,
        "total_distance_meters": instance.total_distance_meters,
        "total_travel_time_seconds": instance.total_travel_time_seconds,
    }


def serialize_route_solutions(instances: List[RouteSolution], ctx: ServiceContext):
    unpacked_instances = [serialize_route_solution(instance) for instance in instances]
    return map_return_values(unpacked_instances, ctx, "route_solution")


def serialize_route_solutions_mixed(
    selected_solution: RouteSolution,
    other_solutions: List[RouteSolution],
    ctx: ServiceContext,
):

    unpacked_instances = [serialize_route_solution(selected_solution)]
    unpacked_instances.extend(
        serialize_route_solution_partial(instance) for instance in other_solutions
    )
    return map_return_values(unpacked_instances, ctx, "route_solution")
