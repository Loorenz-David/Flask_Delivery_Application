from __future__ import annotations

from typing import List, Tuple

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import LocalDeliveryPlan, db
from Delivery_app_BK.route_optimization.constants.skip_reasons import (
    ORDER_CREATED_AFTER_OPTIMIZATION,
)
from ....context import ServiceContext
from Delivery_app_BK.services.commands.route_solution.stops import (
    build_route_solution_stops,
)


def apply_local_delivery_objective(
    ctx: ServiceContext,
    order_instance,
    delivery_plan,
    plan_objective: str,
) -> Tuple[List[object], List[Tuple[object, object]]]:
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

    return stop_instances + updated_solutions, stop_links


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
