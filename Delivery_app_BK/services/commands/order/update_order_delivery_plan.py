from sqlalchemy.orm.exc import NoResultFound

from Delivery_app_BK.errors import NotFound
from Delivery_app_BK.models import db, Order, DeliveryPlan, RouteSolutionStop
from ...context import ServiceContext
from ...domain.order.order_events import OrderEvent
from ...queries.get_instance import get_instance
from ..utils import build_create_result
from .event_emitter import emit_order_events
from .plan_changes import apply_order_plan_change


def update_order_delivery_plan(
    ctx: ServiceContext,
    order_id: int | str,
    plan_id: int | str,
):
    plan_instance_id = None
    try:
        order_instance: Order = get_instance(ctx, Order, order_id)
        old_plan = None
        if order_instance.delivery_plan_id:
            # order instance already has access to the delivery plan 
            old_plan:DeliveryPlan = get_instance(ctx, DeliveryPlan, order_instance.delivery_plan_id)

        new_plan = None
        if isinstance(plan_id, int):
            new_plan:DeliveryPlan = get_instance(ctx, DeliveryPlan, plan_id)
            plan_instance_id = new_plan.id

    except NoResultFound as exc:
        raise NotFound(str(exc)) from exc

    if order_instance.delivery_plan_id == plan_instance_id:
        ctx.set_warning("Order plan is already in the plan that was provided on update")
        return {"order": order_instance.id}

    order_instance.delivery_plan_id = plan_instance_id
    order_instance.order_plan_objective = new_plan.plan_type

    extra_instances, route_stop_links = apply_order_plan_change(
        ctx,
        order_instance,
        old_plan,
        new_plan,
    )

    route_stop_instances = [
        instance
        for instance in extra_instances
        if isinstance(instance, RouteSolutionStop)
    ]

    if extra_instances:
        db.session.add_all(extra_instances)

    db.session.flush()

    if route_stop_links:
        for stop_instance, order_instance in route_stop_links:
            stop_instance.order_id = order_instance.id

    route_stop_results = (
        build_create_result(
            ctx,
            route_stop_instances,
            extract_fields=[
                "id",
                "client_id",
                "route_solution_id",
                "order_id",
                "stop_order",
                "reason_was_skipped",
                "eta_status"
            ],
        )
        if route_stop_instances
        else None
    )

    db.session.commit()
    result = {"order": order_instance.id}
    if route_stop_results is not None:
        result["order_stop"] = route_stop_results

    emit_order_events(
        ctx,
        [
            {
                "order_id": order_instance.id,
                "event_name": OrderEvent.DELIVERY_PLAN_CHANGED.value,
                "payload": {
                    "old_delivery_plan_id": old_plan.id if old_plan else None,
                    "new_delivery_plan_id": new_plan.id if new_plan else None,
                    "new_plan_type": new_plan.plan_type if new_plan else None,
                },
                "team_id": order_instance.team_id,
            }
        ],
    )

    return result
