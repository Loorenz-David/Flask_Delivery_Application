from typing import List
from datetime import datetime, timezone

from Delivery_app_BK.errors import ValidationFailed, NotFound
from Delivery_app_BK.models import RouteSolution, RouteSolutionStop,DeliveryPlan, db
from Delivery_app_BK.directions import refresh_route_solution
from Delivery_app_BK.route_optimization.constants.is_optimized import (
    IS_OPTIMIZED_NOT_OPTIMIZED,
    IS_OPTIMIZED_OPTIMIZE,
    IS_OPTIMIZED_PARTIAL,
)
from ....context import ServiceContext
from ....queries.get_instance import get_instance
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
    time_zone:str = None
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
    created_new_solution = False

    if route_solution.is_optimized == IS_OPTIMIZED_OPTIMIZE:
        route_solution, stop_map, original_route_solution = clone_route_solution(
            route_solution
        )
        created_new_solution = True

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



    if position < current_position:
        for stop in stops:
            if stop.order_id == route_stop.order_id:
                continue
            if position <= (stop.stop_order or 0) < current_position:
                stop.stop_order = (stop.stop_order or 0) + 1
                stop.eta_status = "estimated"
    else:
        for stop in stops:

            if stop.order_id == route_stop.order_id:

                continue
            if current_position < (stop.stop_order or 0) <= position:
                stop.stop_order = (stop.stop_order or 0) - 1
                stop.eta_status = "estimated"


    route_stop.stop_order = position
    route_stop.eta_status = "estimated"
    route_solution.stop_count = len(stops)


    if route_solution.is_optimized == IS_OPTIMIZED_NOT_OPTIMIZED:
        db.session.add_all(stops)
        db.session.commit()
        return {
            "route_solution_stops": [serialize_stop_short(stop) for stop in stops],
        }

    route_solution.is_optimized = IS_OPTIMIZED_PARTIAL
    

    refresh_route_solution(route_solution, time_zone=time_zone)
  
    db.session.add(route_solution)
    db.session.add_all(stops)
    if original_route_solution is not None:
        db.session.add(original_route_solution)
    db.session.commit()

    return {
        "route_solution": serialize_route_solutions([route_solution], ctx),
        "route_solution_stops": serialize_route_solution_stops(stops, ctx),
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
