from __future__ import annotations

from collections.abc import Callable

from Delivery_app_BK.models import DeliveryPlan, Order
from Delivery_app_BK.services.queries.get_instance import get_instance

from ....context import ServiceContext
from .local_delivery import apply_local_delivery_objective
from .types import PlanObjectiveCreateResult


PlanObjectiveHandler = Callable[
    [ServiceContext, Order, DeliveryPlan, str],
    PlanObjectiveCreateResult,
]


PLAN_OBJECTIVE_HANDLERS = {
    "local_delivery": apply_local_delivery_objective,
}


def apply_order_plan_objective(
    ctx: ServiceContext,
    order_instance: Order,
    delivery_plan_id: int | None = None,
    plan_objective: str | None = None,
    delivery_plan: DeliveryPlan | None = None,
) -> PlanObjectiveCreateResult:
    if not delivery_plan and not delivery_plan_id:
        return PlanObjectiveCreateResult()

    if delivery_plan is None:
        delivery_plan = get_instance(
            ctx=ctx,
            model=DeliveryPlan,
            value=delivery_plan_id,
        )

    effective_objective = (
        order_instance.order_plan_objective
        or plan_objective
        or delivery_plan.plan_type
    )
    if not order_instance.order_plan_objective:
        order_instance.order_plan_objective = effective_objective

    handler: PlanObjectiveHandler | None = PLAN_OBJECTIVE_HANDLERS.get(
        delivery_plan.plan_type
    )
    if not handler:
        return PlanObjectiveCreateResult()

    return handler(ctx, order_instance, delivery_plan, effective_objective)
