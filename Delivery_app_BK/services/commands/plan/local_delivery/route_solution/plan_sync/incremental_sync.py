from __future__ import annotations

from collections.abc import Callable
from typing import Any

from Delivery_app_BK.directions import refresh_route_solution_incremental
from Delivery_app_BK.models import RouteSolutionStop
from Delivery_app_BK.services.context import ServiceContext


def build_incremental_route_sync_action(
    *,
    ctx: ServiceContext,
    starts_by_route_id: dict[int, int],
    route_solutions_by_id: dict[int, Any],
    synced_stops: list[RouteSolutionStop],
    changed_route_solutions: list[Any] | None = None,
    orders_by_route_solution_resolver: Callable[[Any], dict[int, Any]] | None = None,
) -> Callable[[], None]:
    def _sync() -> None:
        for route_id, start_position in starts_by_route_id.items():
            route_solution = route_solutions_by_id.get(route_id)
            if not route_solution:
                continue

            orders_by_id = (
                orders_by_route_solution_resolver(route_solution)
                if orders_by_route_solution_resolver
                else _default_orders_by_route_solution(route_solution)
            )

            try:
                changed_stops = refresh_route_solution_incremental(
                    route_solution=route_solution,
                    orders_by_id=orders_by_id,
                    recompute_from_position=start_position,
                    time_zone=ctx.time_zone,
                )
                synced_stops.extend(changed_stops or [])
                if changed_route_solutions is not None:
                    changed_route_solutions.append(route_solution)
            except Exception as exc:
                synced_stops.extend(mark_route_stops_stale(route_solution, start_position))
                if changed_route_solutions is not None:
                    changed_route_solutions.append(route_solution)
                ctx.set_warning(
                    f"Route timings could not be refreshed for route {route_solution.id}: {exc}"
                )

    return _sync


def mark_route_stops_stale(route_solution: Any, start_position: int) -> list[RouteSolutionStop]:
    start_position = max(1, int(start_position or 1))
    route_solution.end_leg_polyline = None
    if start_position <= 1:
        route_solution.start_leg_polyline = None

    changed_stops: list[RouteSolutionStop] = []
    anchor_position = start_position - 1
    for stop in route_solution.stops or []:
        order = stop.stop_order or 0
        if order >= start_position:
            stop.expected_arrival_time = None
            stop.eta_status = "stale"
            stop.in_range = False
            stop.reason_was_skipped = "Route timing unavailable"
            stop.has_constraint_violation = False
            stop.constraint_warnings = None
            stop.to_next_polyline = None
            changed_stops.append(stop)
        elif anchor_position >= 1 and order == anchor_position:
            stop.to_next_polyline = None
            changed_stops.append(stop)

    return changed_stops


def _default_orders_by_route_solution(route_solution: Any) -> dict[int, Any]:
    delivery_plan = None
    if getattr(route_solution, "local_delivery_plan", None):
        delivery_plan = route_solution.local_delivery_plan.delivery_plan

    return {
        order.id: order
        for order in ((delivery_plan.orders or []) if delivery_plan else [])
        if getattr(order, "id", None) is not None
    }

