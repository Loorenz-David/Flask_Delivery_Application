from typing import List
from datetime import datetime, timezone

from Delivery_app_BK.errors import ValidationFailed, NotFound
from Delivery_app_BK.models import RouteSolution, RouteSolutionStop,DeliveryPlan, db
from Delivery_app_BK.directions import refresh_route_solution_incremental
from Delivery_app_BK.route_optimization.constants.is_optimized import (
    IS_OPTIMIZED_NOT_OPTIMIZED,
    IS_OPTIMIZED_OPTIMIZE,
    IS_OPTIMIZED_PARTIAL,
)
from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.queries.get_instance import get_instance
from Delivery_app_BK.services.queries.route_solutions import (
    serialize_route_solution_stops,
    serialize_route_solutions,
)
from ..clone import clone_route_solution
from ..serializers import (
    serialize_stop_short,
)


def _ensure_utc(value: datetime | None) -> datetime | None:
    if not value:
        return None
    return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)


def update_route_stop_position(
    ctx: ServiceContext,
    route_stop_id: int,
    position: int,
):

    if position < 1:
        raise ValidationFailed("position must be a positive integer.")

    route_stop: RouteSolutionStop = get_instance(
        ctx=ctx,
        model=RouteSolutionStop,
        value=route_stop_id,
    )
    if not route_stop.route_solution_id:
        raise ValidationFailed("Route stop is missing route_solution_id.")

    route_solution: RouteSolution = get_instance(
        ctx=ctx,
        model=RouteSolution,
        value=route_stop.route_solution_id,
    )


    _is_route_solution_end_date_valid(route_solution)
    

    original_route_solution = None

    if route_solution.is_optimized == IS_OPTIMIZED_OPTIMIZE:
        route_solution, stop_map, original_route_solution = clone_route_solution(
            route_solution
        )

        route_stop = stop_map.get(route_stop.id)

        if not route_stop:
            raise ValidationFailed("Route stop not found on route solution.")

    stops: List[RouteSolutionStop] = list(route_solution.stops or [])

    if not stops:
        raise ValidationFailed("Route solution has no stops to reorder.")

    if route_stop.stop_order is None:
        raise ValidationFailed("Route stop has no stop_order to update.")

    max_position = max(stop.stop_order or 0 for stop in stops)


    if position > max_position:
        raise ValidationFailed("position exceeds the current stop range.")

    current_position = route_stop.stop_order
    if position == current_position:

        return {
            "route_solution": serialize_route_solutions([route_solution], ctx),
            "route_solution_stops": [],
        }


    touched_stops: list[RouteSolutionStop] = [route_stop]

    if position < current_position:
        for stop in stops:
            if stop.order_id == route_stop.order_id:
                continue
            if position <= (stop.stop_order or 0) < current_position:
                stop.stop_order = (stop.stop_order or 0) + 1
                stop.eta_status = "estimated"
                touched_stops.append(stop)
    else:
        for stop in stops:

            if stop.order_id == route_stop.order_id:

                continue
            if current_position < (stop.stop_order or 0) <= position:
                stop.stop_order = (stop.stop_order or 0) - 1
                stop.eta_status = "estimated"
                touched_stops.append(stop)


    route_stop.stop_order = position
    route_stop.eta_status = "estimated"
    route_solution.stop_count = len(stops)
    affected_start_position = min(current_position, position)


    if route_solution.is_optimized != IS_OPTIMIZED_NOT_OPTIMIZED:
        route_solution.is_optimized = IS_OPTIMIZED_PARTIAL
    
    effective_time_zone = ctx.time_zone
    orders_by_id = _orders_by_id_for_route_solution(route_solution)
    try:
        refreshed_stops = refresh_route_solution_incremental(
            route_solution=route_solution,
            time_zone=effective_time_zone,
            orders_by_id=orders_by_id,
            recompute_from_position=affected_start_position,
        )
    except Exception as exc:
        _mark_suffix_as_stale(route_solution, affected_start_position)
        refreshed_stops = []
        ctx.set_warning(
            f"Route timings could not be refreshed after stop reorder: {exc}"
        )

   
  
    db.session.add(route_solution)
    db.session.add_all(_dedupe_and_sort_stops(touched_stops + refreshed_stops))
    if original_route_solution is not None:
        db.session.add(original_route_solution)
    db.session.commit()

    return {
        "route_solution": serialize_route_solutions([route_solution], ctx),
        "route_solution_stops": serialize_route_solution_stops(
            _dedupe_and_sort_stops(touched_stops + refreshed_stops),
            ctx,
        ),
    }



def _is_route_solution_end_date_valid (route_solution:RouteSolution):
    try:
        delivery_plan:DeliveryPlan = route_solution.local_delivery_plan.delivery_plan
        if delivery_plan:
            now = datetime.now(timezone.utc)
            start_date = _ensure_utc(delivery_plan.start_date) or now
            end_date = _ensure_utc(delivery_plan.end_date) or start_date
            
    except Exception:
        raise NotFound('route solution has no local delivery or local delivery plan has no delivery plan linked.')
    
    if end_date < now:
        raise ValidationFailed('This route has already finished and its stop order cannot be changed. Update the delivery plan end date to a future time to modify the stop order.')


def _orders_by_id_for_route_solution(route_solution: RouteSolution) -> dict[int, object]:
    delivery_plan = None
    if route_solution.local_delivery_plan:
        delivery_plan = route_solution.local_delivery_plan.delivery_plan
    if not delivery_plan:
        return {}

    return {
        order.id: order
        for order in (delivery_plan.orders or [])
        if getattr(order, "id", None) is not None
    }


def _dedupe_and_sort_stops(stops: list[RouteSolutionStop]) -> list[RouteSolutionStop]:
    deduped: list[RouteSolutionStop] = []
    seen: set[int] = set()
    for stop in stops:
        stop_id = getattr(stop, "id", None)
        if stop_id in seen:
            continue
        if stop_id is not None:
            seen.add(stop_id)
        deduped.append(stop)
    return sorted(
        deduped,
        key=lambda stop: stop.stop_order if stop.stop_order is not None else 0,
    )


def _mark_suffix_as_stale(route_solution: RouteSolution, start_position: int) -> None:
    start_position = max(1, int(start_position or 1))
    route_solution.end_leg_polyline = None
    if start_position <= 1:
        route_solution.start_leg_polyline = None

    anchor_position = start_position - 1
    for stop in route_solution.stops or []:
        stop_order = stop.stop_order or 0
        if stop_order >= start_position:
            stop.expected_arrival_time = None
            stop.eta_status = "stale"
            stop.in_range = False
            stop.reason_was_skipped = "Route timing unavailable"
            stop.has_constraint_violation = False
            stop.constraint_warnings = None
            stop.to_next_polyline = None
        elif anchor_position >= 1 and stop_order == anchor_position:
            stop.to_next_polyline = None
