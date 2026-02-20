from Delivery_app_BK.errors import NotFound, ValidationFailed
from Delivery_app_BK.models import RouteSolution

from ...context import ServiceContext
from ..get_instance import get_instance
from .serialize_route_solutions import serialize_route_solutions
from .serialize_route_solution_stops import serialize_route_solution_stops


def get_route_solution(route_solution_id: int, ctx: ServiceContext, return_stops: bool = False):
    if route_solution_id is None:
        raise ValidationFailed("Missing route_solution_id.")
    found_solution = get_instance(
        ctx=ctx,
        model=RouteSolution,
        value=route_solution_id,
    )

    if not found_solution:
        raise NotFound(f"Route solution with id: {route_solution_id} does not exist.")

    if not getattr(found_solution, "is_selected", False):
        raise ValidationFailed("Route solution is not selected.")

    serialized = serialize_route_solutions(
        instances=[found_solution],
        ctx=ctx,
    )

    response = {
        "route_solution": serialized[0] if isinstance(serialized, list) else serialized
    }

    if return_stops:
        stops = list(found_solution.stops or [])
        response["route_solution_stop"] = serialize_route_solution_stops(stops, ctx)

    return response
