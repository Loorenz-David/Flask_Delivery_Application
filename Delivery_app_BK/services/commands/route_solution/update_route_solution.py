from __future__ import annotations

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import RouteSolution, db

from ...context import ServiceContext
from ...queries.get_instance import get_instance
from ..base.update_instance import update_instance
from .update_route_solution_address import update_route_solution_address
from .update_route_solution_times import update_route_solution_times


ALLOWED_FIELDS = {
    "label",
    "is_selected",
    "driver_id"
}
ADDRESS_FIELDS = {"start_location", "end_location"}
TIME_FIELDS = {"set_start_time", "set_end_time"}


def update_route_solution(ctx: ServiceContext):
    incoming_data = ctx.incoming_data or {}
    has_address_fields = any(field in incoming_data for field in ADDRESS_FIELDS)
    has_time_fields = any(field in incoming_data for field in TIME_FIELDS)

    if has_address_fields and has_time_fields:
        raise ValidationFailed(
            "Use separate requests for address and time updates."
        )

    if has_address_fields:
        return update_route_solution_address(ctx)

    if has_time_fields:
        return update_route_solution_times(ctx)

    route_solution_id = incoming_data.get("route_solution_id")
    if not route_solution_id:
        raise ValidationFailed("route_solution_id is required.")

    fields = {key: value for key, value in incoming_data.items() if key in ALLOWED_FIELDS}
    if not fields:
        raise ValidationFailed("No valid fields provided for update.")

    route_solution = get_instance(ctx=ctx, model=RouteSolution, value=route_solution_id)
    update_instance(ctx, RouteSolution, fields, route_solution.id)

    db.session.commit()
    return {"route_solution": route_solution.id}
