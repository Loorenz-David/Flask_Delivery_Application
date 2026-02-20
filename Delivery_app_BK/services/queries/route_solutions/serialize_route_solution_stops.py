from typing import List

from Delivery_app_BK.models import RouteSolutionStop

from ...context import ServiceContext
from ..utils import map_return_values


def serialize_route_solution_stops(instances: List[RouteSolutionStop], ctx: ServiceContext):
    unpacked_instances = []

    for instance in instances:
        expected_arrival_time = instance.expected_arrival_time
        unpacked_instances.append(
            {
                "id": instance.id,
                "client_id": instance.client_id,
                "route_solution_id": instance.route_solution_id,
                "order_id": instance.order_id,
                "service_duration": instance.service_duration,
                "in_range": instance.in_range,
                "stop_order": instance.stop_order,
                "reason_was_skipped": instance.reason_was_skipped,
                "has_constraint_violation": instance.has_constraint_violation,
                "constraint_warnings": instance.constraint_warnings,
                "eta_status": instance.eta_status,
                "expected_arrival_time": expected_arrival_time.isoformat() if expected_arrival_time else None,
                "actual_arrival_time": instance.actual_arrival_time,
            }
        )

    return map_return_values(unpacked_instances, ctx, "route_solution_stop")
