from __future__ import annotations

from collections.abc import Callable

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import DeliveryPlan, RouteSolutionStop
from Delivery_app_BK.directions import refresh_route_solution_incremental
from Delivery_app_BK.route_optimization.constants.is_optimized import (
    IS_OPTIMIZED_OPTIMIZE,
    IS_OPTIMIZED_PARTIAL,
)
from Delivery_app_BK.route_optimization.constants.skip_reasons import (
    ORDER_CHANGE_DELIVERY_PLAN_AFTER_OPTIMIZATION,
)
from Delivery_app_BK.services.commands.order.create_serializers import (
    serialize_created_order_stops,
)
from Delivery_app_BK.services.commands.plan.local_delivery.route_solution.stops import (
    build_route_solution_stops,
    remove_order_stops_for_local_delivery,
)

from ....context import ServiceContext
from .types import PlanChangeApplyContext, PlanChangeResult


def apply_local_delivery_plan_change(
    ctx: ServiceContext,
    order_instance,
    old_plan: DeliveryPlan | None,
    new_plan: DeliveryPlan | None,
    apply_context: PlanChangeApplyContext,
) -> PlanChangeResult:
    instances: list[object] = []
    post_flush_actions: list[Callable[[], None]] = []
    created_stops: list[RouteSolutionStop] = []
    starts_by_route_id: dict[int, int] = {}

    if old_plan and getattr(old_plan, "plan_type", None) == "local_delivery":
        old_local_delivery = apply_context.local_delivery_by_plan_id.get(old_plan.id)
        if not old_local_delivery:
            raise ValidationFailed("Local delivery plan not found for order change.")

        (
            updated_old_stops,
            updated_old_solutions,
            removed_starts_by_route_id,
        ) = remove_order_stops_for_local_delivery(
            order_instance.id,
            old_local_delivery.id,
        )
        instances.extend(updated_old_stops)
        instances.extend(updated_old_solutions)
        for route_id, start_position in removed_starts_by_route_id.items():
            current = starts_by_route_id.get(route_id)
            starts_by_route_id[route_id] = (
                start_position if current is None else min(current, start_position)
            )

    if new_plan and getattr(new_plan, "plan_type", None) == "local_delivery":
        new_local_delivery = apply_context.local_delivery_by_plan_id.get(new_plan.id)
        if not new_local_delivery:
            raise ValidationFailed("Local delivery plan not found for order change.")

        route_solutions = list(
            apply_context.route_solutions_by_local_delivery_id.get(new_local_delivery.id)
            or []
        )
        if not route_solutions:
            raise ValidationFailed("Route solution not found for local delivery plan.")

        stop_instances, stop_links, updated_solutions = build_route_solution_stops(
            ctx,
            order_instance,
            route_solutions,
            skip_reason_for_optimized=ORDER_CHANGE_DELIVERY_PLAN_AFTER_OPTIMIZATION,
        )
        created_stops.extend(stop_instances)
        instances.extend(stop_instances)
        instances.extend(updated_solutions)
        for stop_instance in stop_instances:
            route_id = stop_instance.route_solution_id
            if route_id is None:
                continue
            stop_order = stop_instance.stop_order or 1
            current = starts_by_route_id.get(route_id)
            starts_by_route_id[route_id] = (
                stop_order if current is None else min(current, stop_order)
            )
        post_flush_actions.extend(
            _build_stop_order_link_action(stop_instance, order_instance)
            for stop_instance, order_instance in stop_links
        )

    if starts_by_route_id:
        post_flush_actions.append(
            _build_incremental_route_sync_action(
                ctx=ctx,
                apply_context=apply_context,
                starts_by_route_id=starts_by_route_id,
            )
        )

    return PlanChangeResult(
        instances=instances,
        post_flush_actions=post_flush_actions,
        bundle_serializer=lambda stops=created_stops: _serialize_stop_bundle(stops),
    )


def _serialize_stop_bundle(stops: list[RouteSolutionStop]) -> dict:
    if not stops:
        return {}
    return {"order_stops": serialize_created_order_stops(stops)}


def _build_stop_order_link_action(
    stop_instance: RouteSolutionStop,
    order_instance,
) -> Callable[[], None]:
    def _link() -> None:
        stop_instance.order_id = order_instance.id

    return _link


def _build_incremental_route_sync_action(
    ctx: ServiceContext,
    apply_context: PlanChangeApplyContext,
    starts_by_route_id: dict[int, int],
) -> Callable[[], None]:
    route_solutions_by_id: dict[int, object] = {}
    for route_solutions in apply_context.route_solutions_by_local_delivery_id.values():
        for route_solution in route_solutions:
            if getattr(route_solution, "id", None) is None:
                continue
            route_solutions_by_id[route_solution.id] = route_solution

    def _sync() -> None:
        for route_id, start_position in starts_by_route_id.items():
            route_solution = route_solutions_by_id.get(route_id)
            if not route_solution:
                continue
            if route_solution.is_optimized not in {IS_OPTIMIZED_OPTIMIZE, IS_OPTIMIZED_PARTIAL}:
                continue
            delivery_plan = None
            if route_solution.local_delivery_plan:
                delivery_plan = route_solution.local_delivery_plan.delivery_plan
            orders_by_id = {
                order.id: order
                for order in ((delivery_plan.orders or []) if delivery_plan else [])
                if getattr(order, "id", None) is not None
            }
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
