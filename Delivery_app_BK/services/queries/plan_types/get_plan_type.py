from Delivery_app_BK.models import DeliveryPlan
from Delivery_app_BK.errors import NotFound

from ...context import ServiceContext
from ..get_instance import get_instance
from .serialize_local_delivery_plan import serialize_local_delivery_plan
from .serialize_international_shipping_plan import serialize_international_shipping_plan
from .serialize_store_pickup_plan import serialize_store_pickup_plan


def get_plan_type(plan_id: int, plan_type: str, ctx: ServiceContext):
    found_plan:DeliveryPlan = get_instance(
        ctx=ctx,
        model=DeliveryPlan,
        value=plan_id,
    )

    if not found_plan:
        raise NotFound(f"Delivery plan with id: {plan_id} does not exist.")

    if plan_type == "local_delivery":
        delivery_type_instance = found_plan.local_delivery
        serialized = (
            serialize_local_delivery_plan(delivery_type_instance, ctx)
            if delivery_type_instance
            else None
        )
    elif plan_type == "international_shipping":
        delivery_type_instance = found_plan.international_shipping
        serialized = (
            serialize_international_shipping_plan(delivery_type_instance, ctx)
            if delivery_type_instance
            else None
        )
    elif plan_type == "store_pickup":
        delivery_type_instance = found_plan.store_pickup
        serialized = (
            serialize_store_pickup_plan(delivery_type_instance, ctx)
            if delivery_type_instance
            else None
        )
    else:
        raise NotFound(f"Unknown delivery plan type: {plan_type}")

    return {
        "delivery_plan_type": serialized
    }
