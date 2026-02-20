from __future__ import annotations

from typing import Dict, Tuple

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import RouteSolution, RouteSolutionStop
from Delivery_app_BK.route_optimization.constants.is_optimized import IS_OPTIMIZED_PARTIAL
from Delivery_app_BK.services.commands.utils import generate_client_id


def clone_route_solution(
    route_solution: RouteSolution,
) -> Tuple[RouteSolution, Dict[int, RouteSolutionStop], RouteSolution]:
    local_delivery_plan = route_solution.local_delivery_plan
    if not local_delivery_plan:
        raise ValidationFailed("Route solution has no local delivery plan.")

    original = route_solution
    original.is_selected = False
    original.is_optimized = IS_OPTIMIZED_PARTIAL

    route_solution_count = len(local_delivery_plan.route_solutions or [])
    new_route_solution = RouteSolution(
        client_id=generate_client_id('route_solution'),
        label=f"variant {route_solution_count + 1}",
        version=route_solution.version,
        algorithm=route_solution.algorithm,
        score=route_solution.score,
        total_distance_meters=route_solution.total_distance_meters,
        total_travel_time_seconds=route_solution.total_travel_time_seconds,
        expected_start_time=route_solution.expected_start_time,
        expected_end_time=route_solution.expected_end_time,
        has_route_warnings=route_solution.has_route_warnings,
        route_warnings=route_solution.route_warnings,
        start_location=route_solution.start_location,
        end_location=route_solution.end_location,
        set_start_time=route_solution.set_start_time,
        set_end_time=route_solution.set_end_time,
        is_selected=True,
        is_optimized=IS_OPTIMIZED_PARTIAL,
        stop_count=route_solution.stop_count,
        driver_id=route_solution.driver_id,
        local_delivery_plan_id=route_solution.local_delivery_plan_id,
        team_id=route_solution.team_id,
        route_polyline=route_solution.route_polyline,
    )

    stop_map: Dict[int, RouteSolutionStop] = {}
    new_stops = []
    for stop in route_solution.stops or []:
        cloned_stop = RouteSolutionStop(
            client_id=generate_client_id('route_stop'),
            order_id=stop.order_id,
            service_duration=stop.service_duration,
            in_range=stop.in_range,
            stop_order=stop.stop_order,
            reason_was_skipped=stop.reason_was_skipped,
            has_constraint_violation=stop.has_constraint_violation,
            constraint_warnings=stop.constraint_warnings,
            eta_status=stop.eta_status,
            expected_arrival_time=stop.expected_arrival_time,
            actual_arrival_time=stop.actual_arrival_time,
            team_id=stop.team_id,
        )
        stop_map[stop.id] = cloned_stop
        new_stops.append(cloned_stop)

    new_route_solution.stops = new_stops
    new_route_solution.stop_count = len(new_stops)
    local_delivery_plan.route_solutions.append(new_route_solution)

    return new_route_solution, stop_map, original
