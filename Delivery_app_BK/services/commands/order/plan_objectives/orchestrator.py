from __future__ import annotations

from typing import List, Tuple

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import DeliveryPlan,Order
from Delivery_app_BK.services.queries.get_instance import get_instance

from ....context import ServiceContext
from .local_delivery import apply_local_delivery_objective


PLAN_OBJECTIVE_HANDLERS = {
    "local_delivery": apply_local_delivery_objective,
}


def apply_order_plan_objective(
    ctx: ServiceContext,
    order_instance:Order,
    delivery_plan_id: int | None,
    plan_objective: str | None,
) -> Tuple[List[object], List[Tuple[object, object]]]:
    if not delivery_plan_id:
        return [], []
  
    delivery_plan:DeliveryPlan = get_instance(ctx=ctx, model=DeliveryPlan, value=delivery_plan_id)

    if not plan_objective:
        plan_objective = delivery_plan.plan_type
    order_instance.order_plan_objective = plan_objective

    handler = PLAN_OBJECTIVE_HANDLERS.get(delivery_plan.plan_type)
    if not handler:
        return [],[]
        raise ValidationFailed(
            f"No order plan objective handler for plan type {delivery_plan.plan_type}."
        )

    return handler(ctx, order_instance, delivery_plan, plan_objective)
