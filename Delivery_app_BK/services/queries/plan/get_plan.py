from Delivery_app_BK.models import db, DeliveryPlan
from Delivery_app_BK.errors import NotFound

from ...context import ServiceContext
from ..get_instance import get_instance 
from .serialize_plan import serialize_plans


def get_plan(plan_id: int, ctx: ServiceContext):

    found_plan = get_instance(
        ctx = ctx,
        model = DeliveryPlan,
        value = plan_id
    )

    if not found_plan:
        raise NotFound(f"Delivery plan with id: {plan_id} does not exist.")

    serialized = serialize_plans(
        instances=[found_plan],
        ctx=ctx,
    )

    return {
        "delivery_plan": serialized[0] if isinstance(serialized, list) else serialized
    }
