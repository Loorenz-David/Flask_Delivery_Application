from __future__ import annotations

from collections.abc import Callable
from typing import List

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import LocalDeliveryPlan, RouteSolutionStop, db
from Delivery_app_BK.directions import refresh_route_solution_incremental
from Delivery_app_BK.route_optimization.constants.skip_reasons import (
    ORDER_CREATED_AFTER_OPTIMIZATION,
)
from Delivery_app_BK.route_optimization.constants.is_optimized import (
    IS_OPTIMIZED_OPTIMIZE,
    IS_OPTIMIZED_PARTIAL,
)
from Delivery_app_BK.services.commands.order.create_serializers import (
    serialize_created_order_stops,
)
from ....context import ServiceContext
from Delivery_app_BK.services.commands.plan.local_delivery.route_solution.stops import (
    build_route_solution_stops,
)
from .types import PlanObjectiveCreateResult


def apply_local_delivery_objective(
    ctx: ServiceContext,
    order_instance,
    delivery_plan,
    plan_objective: str,
) -> PlanObjectiveCreateResult:
    local_delivery = _get_local_delivery_plan(ctx, delivery_plan.id)
    route_solutions = list(local_delivery.route_solutions or [])
    if not route_solutions:
        raise ValidationFailed("Route solution not found for local delivery plan.")

    stop_instances, stop_links, updated_solutions = build_route_solution_stops(
        ctx,
        order_instance,
        route_solutions,
        skip_reason_for_optimized=_skip_reason_value(ORDER_CREATED_AFTER_OPTIMIZATION),
    )
    post_flush_actions = [
        _build_stop_order_link_action(stop_instance, order_instance)
        for stop_instance, order_instance in stop_links
    ]
    post_flush_actions.append(
        _build_incremental_route_sync_action(
            ctx=ctx,
            delivery_plan=delivery_plan,
            route_solutions=route_solutions,
            created_stops=stop_instances,
        )
    )


    return PlanObjectiveCreateResult(
        instances=stop_instances + updated_solutions,
        post_flush_actions=post_flush_actions,
        bundle_serializer=lambda stops=stop_instances: _serialize_stop_bundle(stops),
    )


def _get_local_delivery_plan(ctx: ServiceContext, delivery_plan_id: int) -> LocalDeliveryPlan:
    query = db.session.query(LocalDeliveryPlan).filter(
        LocalDeliveryPlan.delivery_plan_id == delivery_plan_id
    )
    if ctx.team_id:
        query = query.filter(LocalDeliveryPlan.team_id == ctx.team_id)
    local_delivery = query.one_or_none()
    if not local_delivery:
        raise ValidationFailed("Local delivery plan not found for order objective.")
    return local_delivery


def _skip_reason_value(reason) -> str | None:
    if isinstance(reason, tuple):
        return reason[0] if reason else None
    return reason


def _build_stop_order_link_action(
    stop_instance: RouteSolutionStop,
    order_instance,
) -> Callable[[], None]:
    def _link() -> None:
        stop_instance.order_id = order_instance.id

    return _link


def _serialize_stop_bundle(stops: list[RouteSolutionStop]) -> dict:
    if not stops:
        return {}
    return {"order_stops": serialize_created_order_stops(stops)}


def _build_incremental_route_sync_action(
    ctx: ServiceContext,
    delivery_plan,
    route_solutions: list,
    created_stops: list[RouteSolutionStop],
) -> Callable[[], None]:
    starts_by_route_id: dict[int, int] = {}
    for stop in created_stops:
        route_id = stop.route_solution_id
        if route_id is None:
            continue
        stop_order = stop.stop_order or 1
        current = starts_by_route_id.get(route_id)
        starts_by_route_id[route_id] = stop_order if current is None else min(current, stop_order)

    route_solutions_by_id = {
        route_solution.id: route_solution
        for route_solution in route_solutions
        if getattr(route_solution, "id", None) is not None
    }

    def _sync() -> None:
        orders_by_id = {
            order.id: order
            for order in (delivery_plan.orders or [])
            if getattr(order, "id", None) is not None
        }
        for route_id, start_position in starts_by_route_id.items():
            route_solution = route_solutions_by_id.get(route_id)
            if not route_solution:
                continue
            if route_solution.is_optimized not in {IS_OPTIMIZED_OPTIMIZE, IS_OPTIMIZED_PARTIAL}:
                continue
            try:
                refresh_route_solution_incremental(
                    route_solution=route_solution,
                    orders_by_id=orders_by_id,
                    recompute_from_position=start_position,
                    time_zone=ctx.time_zone,
                )
            except Exception as exc:
                _mark_stops_stale(route_solution, start_position)
                ctx.set_warning(
                    f"Route timings could not be refreshed for route {route_solution.id}: {exc}"
                )

    return _sync


def _mark_stops_stale(route_solution, start_position: int) -> None:
    start_position = max(1, int(start_position or 1))
    route_solution.end_leg_polyline = None
    if start_position <= 1:
        route_solution.start_leg_polyline = None

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
        elif anchor_position >= 1 and order == anchor_position:
            stop.to_next_polyline = None
