from typing import Dict
from datetime import timezone

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import Order, RouteSolution, db
from Delivery_app_BK.route_optimization.constants.is_optimized import (
    IS_OPTIMIZED_NOT_OPTIMIZED,
    IS_OPTIMIZED_OPTIMIZE,
    IS_OPTIMIZED_PARTIAL,
)

from ...context import ServiceContext
from ...queries.get_instance import get_instance
from .clone import clone_route_solution
from Delivery_app_BK.services.queries.route_solutions import (
    serialize_route_solution_stops,
    serialize_route_solutions,
)
from Delivery_app_BK.directions.services.refresher import (
    _build_stop_warnings,
    _resolve_allowed_end,
)


def _ensure_utc(value):
    if not value:
        return None
    return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)


def update_route_solution_times(ctx: ServiceContext):
    incoming_data = ctx.incoming_data or {}
    route_solution_id = incoming_data.get("route_solution_id")
    if not route_solution_id:
        raise ValidationFailed("route_solution_id is required.")

    set_start_time = incoming_data.get("set_start_time")
    set_end_time = incoming_data.get("set_end_time")
    if set_start_time is None and set_end_time is None:
        raise ValidationFailed("set_start_time or set_end_time is required.")

    route_solution: RouteSolution = get_instance(
        ctx=ctx,
        model=RouteSolution,
        value=route_solution_id,
    )

    original_route_solution = None

    if route_solution.is_optimized == IS_OPTIMIZED_OPTIMIZE:
        route_solution, _, original_route_solution = clone_route_solution(route_solution)

    if set_start_time is not None:
        route_solution.set_start_time = set_start_time
    if set_end_time is not None:
        route_solution.set_end_time = set_end_time

    if route_solution.is_optimized != IS_OPTIMIZED_NOT_OPTIMIZED:
        route_solution.is_optimized = IS_OPTIMIZED_PARTIAL

    orders_by_id = _load_orders(route_solution)
    _refresh_time_warnings(route_solution, orders_by_id)

    db.session.add(route_solution)
    db.session.add_all(route_solution.stops or [])
    if original_route_solution is not None:
        db.session.add(original_route_solution)
    db.session.commit()

    return {
        "route_solution": serialize_route_solutions([route_solution], ctx),
        "route_solution_stops": serialize_route_solution_stops(route_solution.stops, ctx),
    }


def _refresh_time_warnings(
    route_solution: RouteSolution,
    orders_by_id: Dict[int, Order],
) -> None:
    allowed_end = _ensure_utc(_resolve_allowed_end(route_solution))
    route_warnings = []
    expected_end = _ensure_utc(route_solution.expected_end_time)
    if allowed_end and expected_end:
        if expected_end > allowed_end:
            from Delivery_app_BK.models.mixins.validation_mixins.time_warning_validation import (
                TimeWarningFactory,
            )
            route_warnings.append(
                TimeWarningFactory.route_end_time_exceeded(
                    expected_end=expected_end,
                    allowed_end=allowed_end,
                )
            )

    route_solution.route_warnings = route_warnings or None
    route_solution.has_route_warnings = bool(route_warnings)

    for stop in route_solution.stops or []:
        order = orders_by_id.get(stop.order_id)
        arrival_time = stop.expected_arrival_time
        warnings = _build_stop_warnings(order, arrival_time, route_solution)
        stop.constraint_warnings = warnings or None
        stop.has_constraint_violation = bool(warnings)


def _load_orders(route_solution: RouteSolution) -> Dict[int, Order]:
    order_ids = [
        stop.order_id
        for stop in (route_solution.stops or [])
        if stop.order_id is not None
    ]
    if not order_ids:
        return {}

    orders = (
        db.session.query(Order)
        .filter(Order.id.in_(order_ids))
        .all()
    )
    return {order.id: order for order in orders}
