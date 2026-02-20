from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import RouteSolution, db
from Delivery_app_BK.directions import refresh_route_solution
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



def update_route_solution_address(ctx: ServiceContext):
    incoming_data = ctx.incoming_data or {}
    route_solution_id = incoming_data.get("route_solution_id")
    if not route_solution_id:
        raise ValidationFailed("route_solution_id is required.")

    start_location = incoming_data.get("start_location")
    end_location = incoming_data.get("end_location")
    if start_location is None and end_location is None:
        raise ValidationFailed("start_location or end_location is required.")

    route_solution: RouteSolution = get_instance(
        ctx=ctx,
        model=RouteSolution,
        value=route_solution_id,
    )

    original_route_solution = None

    if route_solution.is_optimized == IS_OPTIMIZED_OPTIMIZE:
        route_solution, _, original_route_solution = clone_route_solution(route_solution)

    if start_location is not None:
        route_solution.start_location = start_location
    if end_location is not None:
        route_solution.end_location = end_location

    stops = list(route_solution.stops or [])
    if route_solution.is_optimized == IS_OPTIMIZED_NOT_OPTIMIZED:
        db.session.add(route_solution)
        if original_route_solution is not None:
            db.session.add(original_route_solution)
        db.session.commit()
        return {
            "route_solution": serialize_route_solutions([route_solution], ctx),
            "route_solution_stops": [],
        }

    route_solution.is_optimized = IS_OPTIMIZED_PARTIAL
    refresh_route_solution(route_solution)

    db.session.add(route_solution)
    db.session.add_all(stops)
    if original_route_solution is not None:
        db.session.add(original_route_solution)
    db.session.commit()

    return {
        "route_solution": serialize_route_solutions([route_solution], ctx),
        "route_solution_stops": serialize_route_solution_stops(stops, ctx),
    }
