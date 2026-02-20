from __future__ import annotations

from typing import List, Tuple

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import (
    InternationalShippingPlan,
    LocalDeliveryPlan,
    RouteSolution,
    StorePickupPlan,
)
from Delivery_app_BK.route_optimization.constants.is_optimized import (
    IS_OPTIMIZED_NOT_OPTIMIZED,
)
from Delivery_app_BK.services.commands.utils import generate_client_id

from ...context import ServiceContext
from ..base.create_instance import create_instance


PLAN_TYPE_MAP = {
    "local_delivery": LocalDeliveryPlan,
    "international_shipping": InternationalShippingPlan,
    "store_pickup": StorePickupPlan,
}


def build_plan_type_instances(
    ctx: ServiceContext,
    plan_type: str,
    fields_plan_type: dict,
    plan_instance,
) -> Tuple[object, List[object]]:
    if not plan_type:
        raise ValidationFailed("Missing plan_type.")
    if not fields_plan_type:
        raise ValidationFailed(f"Missing fields for plan type {plan_type}.")
    if plan_type not in PLAN_TYPE_MAP:
        raise ValidationFailed(f"Invalid plan_type: {plan_type}")

    plan_type_model = PLAN_TYPE_MAP[plan_type]
    plan_type_instance = create_instance(ctx, plan_type_model, fields_plan_type)
    setattr(plan_instance, plan_type, plan_type_instance)

    extra_instances: List[object] = []

    if plan_type == "local_delivery":
        plan_type_instance: LocalDeliveryPlan
        route_solution = RouteSolution(
            client_id=generate_client_id('route_solution'),
            label="variant 1",
            is_selected=True,
            is_optimized=IS_OPTIMIZED_NOT_OPTIMIZED,
            stop_count=0,
            team_id=ctx.team_id,
        )
        plan_type_instance.route_solutions.append(route_solution)
        extra_instances.append(route_solution)

    return plan_type_instance, extra_instances
