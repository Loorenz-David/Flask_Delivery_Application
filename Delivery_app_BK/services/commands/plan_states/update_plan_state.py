from Delivery_app_BK.models import db, DeliveryPlan, PlanState
from ...context import ServiceContext
from ...queries.get_instance import get_instance


def update_plan_state(ctx: ServiceContext, plan_id: int | str, state_id: int | str):
    plan_instance: DeliveryPlan = get_instance(ctx, DeliveryPlan, plan_id)
    state_instance: PlanState = get_instance(ctx, PlanState, state_id)

    plan_instance.state_id = state_instance.id
    db.session.commit()
    return plan_instance
