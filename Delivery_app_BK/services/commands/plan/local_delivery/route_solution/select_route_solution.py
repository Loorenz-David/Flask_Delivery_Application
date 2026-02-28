from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import RouteSolution, db

from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.queries.get_instance import get_instance
from Delivery_app_BK.services.commands.utils import build_create_result


def select_route_solution(ctx: ServiceContext, route_solution_id: int):
    route_solution = get_instance(
        ctx=ctx,
        model=RouteSolution,
        value=route_solution_id,
    )
    if not route_solution.local_delivery_plan_id:
        raise ValidationFailed("Route solution has no local delivery plan.")

    previous_selected = (
        RouteSolution.query.filter(
            RouteSolution.local_delivery_plan_id == route_solution.local_delivery_plan_id,
            RouteSolution.is_selected.is_(True),
            RouteSolution.id != route_solution.id,
        )
        .first()
    )

    updated = []
    if previous_selected:
        previous_selected.is_selected = False
        updated.append(previous_selected)

    if not route_solution.is_selected:
        route_solution.is_selected = True
    updated.append(route_solution)

    db.session.add_all(updated)
    db.session.commit()

    return {
        "route_solution": build_create_result(
            ctx,
            updated,
            extract_fields=["id", "is_selected"],
        ),
    }
