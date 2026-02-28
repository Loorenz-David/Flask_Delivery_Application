from Delivery_app_BK.models.tables.delivery_plan.delivery_plan import DeliveryPlan, db
from ...context import ServiceContext
from Delivery_app_BK.services.commands.order.order_states.update_orders_state import update_orders_state
from Delivery_app_BK.services.domain.plan.plan_states import PlanStateId
from ...domain.order.order_states import OrderStateId
from Delivery_app_BK.services.queries.get_instance import get_instance



def mark_plan_state(
        ctx:ServiceContext,
        delivery_plan_id: int,
        state_id: PlanStateId
):

        plan:DeliveryPlan = get_instance(ctx, DeliveryPlan,delivery_plan_id)

        if plan.state_id == state_id:
                return {}
        
        plan.state_id = state_id
        orders = plan.orders

        if state_id == PlanStateId.READY:
                update_orders_state(
                        ctx=ctx,
                        orders=orders,
                        state_id=OrderStateId.READY
                )
       

        return {
                "failed_order_state_updates":{}
        }