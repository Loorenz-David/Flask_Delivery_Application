from __future__ import annotations

from collections import defaultdict

from Delivery_app_BK.models import RouteSolution, RouteSolutionStop, db


def remove_order_stops_for_local_delivery(
    order_id: int,
    local_delivery_plan_id: int,
) -> tuple[list[RouteSolutionStop], list[RouteSolution], dict[int, int]]:
    return remove_orders_stops_for_local_delivery([order_id], local_delivery_plan_id)


def remove_orders_stops_for_local_delivery(
    order_ids: list[int],
    local_delivery_plan_id: int,
) -> tuple[list[RouteSolutionStop], list[RouteSolution], dict[int, int]]:
    if not order_ids:
        return [], [], {}

    deduped_order_ids = list(dict.fromkeys(order_ids))
    route_solution_ids = [
        row[0]
        for row in db.session.query(RouteSolution.id)
        .filter(RouteSolution.local_delivery_plan_id == local_delivery_plan_id)
        .all()
    ]
    if not route_solution_ids:
        return [], [], {}

    stops = (
        db.session.query(RouteSolutionStop)
        .filter(RouteSolutionStop.order_id.in_(deduped_order_ids))
        .filter(RouteSolutionStop.route_solution_id.in_(route_solution_ids))
        .all()
    )
    if not stops:
        return [], [], {}

    removed_min_position_by_route: dict[int, int] = {}
    for stop in stops:
        if stop.stop_order is None:
            continue
        current = removed_min_position_by_route.get(stop.route_solution_id)
        removed_min_position_by_route[stop.route_solution_id] = (
            stop.stop_order if current is None else min(current, stop.stop_order)
        )

    stop_counts = defaultdict(int)
    for stop in stops:
        stop_counts[stop.route_solution_id] += 1

    route_solutions = (
        db.session.query(RouteSolution)
        .filter(RouteSolution.id.in_(route_solution_ids))
        .all()
    )
    for route_solution in route_solutions:
        decrement = stop_counts.get(route_solution.id, 0)
        if decrement:
            current = route_solution.stop_count or 0
            route_solution.stop_count = max(0, current - decrement)

    for stop in stops:
        db.session.delete(stop)

    updated_stops: list[RouteSolutionStop] = []
    for route_solution in route_solutions:
        remaining = (
            db.session.query(RouteSolutionStop)
            .filter(RouteSolutionStop.route_solution_id == route_solution.id)
            .order_by(RouteSolutionStop.stop_order)
            .all()
        )
        for index, stop in enumerate(remaining, start=1):
            if stop.stop_order != index:
                stop.stop_order = index
                updated_stops.append(stop)

        if route_solution.stop_count != len(remaining):
            route_solution.stop_count = len(remaining)

    affected_start_by_route: dict[int, int] = {}
    for route_solution in route_solutions:
        route_id = route_solution.id
        updated_min = min(
            (
                stop.stop_order
                for stop in updated_stops
                if stop.route_solution_id == route_id and stop.stop_order is not None
            ),
            default=None,
        )
        removed_min = removed_min_position_by_route.get(route_id)
        candidates = [value for value in (updated_min, removed_min) if value is not None]
        if candidates:
            affected_start_by_route[route_id] = max(1, min(candidates))

    return updated_stops, route_solutions, affected_start_by_route
