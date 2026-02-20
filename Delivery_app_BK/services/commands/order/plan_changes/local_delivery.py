from __future__ import annotations

from typing import List, Tuple

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import LocalDeliveryPlan, DeliveryPlan
from Delivery_app_BK.route_optimization.constants.skip_reasons import (
    ORDER_CHANGE_DELIVERY_PLAN_AFTER_OPTIMIZATION,
)

from ....context import ServiceContext
from ....queries.get_instance import get_instance
from Delivery_app_BK.services.commands.route_solution.stops import (
    build_route_solution_stops,
    remove_order_stops_for_local_delivery,
)


def apply_local_delivery_plan_change(
    ctx: ServiceContext,
    order_instance,
    old_plan: DeliveryPlan,
    new_plan: DeliveryPlan,
) -> Tuple[List[object], List[Tuple[object, object]]]:
    if old_plan and getattr(old_plan, "plan_type", None) == "local_delivery":
        if not old_plan.local_delivery:
            raise ValidationFailed("Local delivery plan not found for order change.")
        old_local_delivery: LocalDeliveryPlan = get_instance(
            ctx=ctx, model=LocalDeliveryPlan, value=old_plan.local_delivery.id
        )
        updated_old_stops, updated_old_solutions = remove_order_stops_for_local_delivery(
            order_instance.id,
            old_local_delivery.id,
        )
    else:
        updated_old_stops, updated_old_solutions = [], []

    if not new_plan or getattr(new_plan, "plan_type", None) != "local_delivery":
        return [], []

    if not new_plan.local_delivery:
        raise ValidationFailed("Local delivery plan not found for order change.")
    new_local_delivery: LocalDeliveryPlan = get_instance(
        ctx=ctx, model=LocalDeliveryPlan, value=new_plan.local_delivery.id
    )
    route_solutions = list(new_local_delivery.route_solutions or [])
    if not route_solutions:
        raise ValidationFailed("Route solution not found for local delivery plan.")

    stop_instances, stop_links, updated_solutions = build_route_solution_stops(
        ctx,
        order_instance,
        route_solutions,
        skip_reason_for_optimized=ORDER_CHANGE_DELIVERY_PLAN_AFTER_OPTIMIZATION,
    )

    return stop_instances + updated_solutions + updated_old_stops + updated_old_solutions, stop_links
