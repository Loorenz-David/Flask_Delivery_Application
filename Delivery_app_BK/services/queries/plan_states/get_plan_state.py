from Delivery_app_BK.models import DeliveryPlanState
from Delivery_app_BK.errors import NotFound

from ...context import ServiceContext
from ..get_instance import get_instance
from .serialize_plan_states import serialize_plan_states


def get_plan_state(state_id: int, ctx: ServiceContext):
    found_state = get_instance(
        ctx=ctx,
        model=DeliveryPlanState,
        value=state_id,
    )

    if not found_state:
        raise NotFound(f"Plan state with id: {state_id} does not exist.")

    serialized = serialize_plan_states(
        instances=[found_state],
        ctx=ctx,
    )

    return {
        "plan_state": serialized[0] if isinstance(serialized, list) else serialized
    }
