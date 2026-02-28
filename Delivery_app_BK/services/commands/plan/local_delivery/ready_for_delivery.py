from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models.tables.delivery_plan.delivery_plan import DeliveryPlan
from Delivery_app_BK.services.commands.order.order_states.update_orders_state import (
    update_orders_state,
)
from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.domain.order.order_states import OrderStateId
from Delivery_app_BK.services.domain.plan.plan_states import PlanStateId
from Delivery_app_BK.services.queries.get_instance import get_instance


def ready_for_delivery(
    ctx: ServiceContext,
    delivery_plan_id: int,
) -> dict:
    delivery_plan: DeliveryPlan = get_instance(
        ctx=ctx,
        model=DeliveryPlan,
        value=delivery_plan_id,
    )
    if delivery_plan.plan_type != "local_delivery":
        raise ValidationFailed(
            "ready_for_delivery is only available for local_delivery plans."
        )

    if delivery_plan.state_id == PlanStateId.READY:
        return {}

    delivery_plan.state_id = PlanStateId.READY
    update_orders_state(
        ctx=ctx,
        orders=delivery_plan.orders or [],
        state_id=OrderStateId.READY,
    )

    return {"failed_order_state_updates": {}}
