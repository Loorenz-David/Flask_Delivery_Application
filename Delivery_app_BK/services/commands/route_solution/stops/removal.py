from __future__ import annotations

from collections import defaultdict

from Delivery_app_BK.models import RouteSolution, RouteSolutionStop, db


def remove_order_stops_for_local_delivery(
    order_id: int,
    local_delivery_plan_id: int,
) -> tuple[list[RouteSolutionStop], list[RouteSolution]]:
    route_solution_ids = [
        row[0]
        for row in db.session.query(RouteSolution.id)
        .filter(RouteSolution.local_delivery_plan_id == local_delivery_plan_id)
        .all()
    ]
    if not route_solution_ids:
        return [], []

    stops = (
        db.session.query(RouteSolutionStop)
        .filter(RouteSolutionStop.order_id == order_id)
        .filter(RouteSolutionStop.route_solution_id.in_(route_solution_ids))
        .all()
    )
    if not stops:
        return [], []

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

    return updated_stops, route_solutions
