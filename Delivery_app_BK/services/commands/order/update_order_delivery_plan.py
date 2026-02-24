from sqlalchemy.orm.exc import NoResultFound

from Delivery_app_BK.errors import NotFound, ValidationFailed
from Delivery_app_BK.models import db, Order, DeliveryPlan, RouteSolutionStop, LocalDeliveryPlan
from Delivery_app_BK.route_optimization.constants.skip_reasons import (
    ORDER_CHANGE_DELIVERY_PLAN_AFTER_OPTIMIZATION,
)
from ...context import ServiceContext
from ...domain.order.order_events import OrderEvent
from ...queries.get_instance import get_instance
from ..utils import build_create_result
from .event_emitter import emit_order_events
from ..route_solution.stops import (
    build_route_solution_stops_for_order_ids,
    remove_orders_stops_for_local_delivery,
)


def apply_orders_delivery_plan_change(
    ctx: ServiceContext,
    order_ids: list[int | str],
    plan_id: int | str,
) -> dict:
    deduped_order_ids = list(dict.fromkeys(order_ids))
    if not deduped_order_ids:
        return {
            "order_ids": [],
            "route_stop_instances": [],
            "pending_events": [],
        }

    try:
        new_plan: DeliveryPlan = get_instance(ctx, DeliveryPlan, plan_id)
    except NoResultFound as exc:
        raise NotFound(str(exc)) from exc

    int_order_ids = [order_id for order_id in deduped_order_ids if isinstance(order_id, int)]
    client_order_ids = [order_id for order_id in deduped_order_ids if isinstance(order_id, str)]

    orders_by_id: dict[int, Order] = {}
    orders_by_client_id: dict[str, Order] = {}

    if int_order_ids:
        orders = (
            db.session.query(Order)
            .filter(Order.id.in_(int_order_ids))
            .with_for_update()
            .all()
        )
        orders_by_id = {order.id: order for order in orders}

    if client_order_ids:
        client_orders = (
            db.session.query(Order)
            .filter(Order.client_id.in_(client_order_ids))
            .with_for_update()
            .all()
        )
        orders_by_client_id = {order.client_id: order for order in client_orders}

    missing_ids = [
        order_id
        for order_id in deduped_order_ids
        if (
            (isinstance(order_id, int) and order_id not in orders_by_id)
            or (isinstance(order_id, str) and order_id not in orders_by_client_id)
        )
    ]
    if missing_ids:
        raise NotFound(f"Orders not found: {missing_ids}")

    pending_events: list[dict] = []
    changed_orders: list[Order] = []
    old_plan_ids: set[int] = set()
    orders_by_old_plan: dict[int, list[Order]] = {}
    old_plan_by_order_id: dict[int, int | None] = {}
    route_stop_instances: list[RouteSolutionStop] = []
    extra_instances: list[object] = []

    for order_id in deduped_order_ids:
        order_instance = (
            orders_by_id[order_id]
            if isinstance(order_id, int)
            else orders_by_client_id[order_id]
        )
        get_instance(ctx, Order, order_instance)

        old_plan_id = order_instance.delivery_plan_id
        if old_plan_id == new_plan.id:
            ctx.set_warning("Order plan is already in the plan that was provided on update")
            continue

        old_plan_ids.add(old_plan_id) if old_plan_id else None
        if old_plan_id:
            orders_by_old_plan.setdefault(old_plan_id, []).append(order_instance)

        order_instance.delivery_plan_id = new_plan.id
        order_instance.order_plan_objective = new_plan.plan_type
        old_plan_by_order_id[order_instance.id] = old_plan_id
        changed_orders.append(order_instance)

    if not changed_orders:
        return {
            "order_ids": [],
            "route_stop_instances": [],
            "pending_events": [],
        }

    old_plans_by_id: dict[int, DeliveryPlan] = {}
    if old_plan_ids:
        old_plans = db.session.query(DeliveryPlan).filter(DeliveryPlan.id.in_(list(old_plan_ids))).all()
        old_plans_by_id = {plan.id: plan for plan in old_plans}

    for old_plan_id, plan_orders in orders_by_old_plan.items():
        old_plan = old_plans_by_id.get(old_plan_id)
        if not old_plan:
            continue
        if getattr(old_plan, "plan_type", None) != "local_delivery":
            continue

        old_local_delivery = _get_local_delivery_plan_by_delivery_plan_id(ctx, old_plan.id)
        if not old_local_delivery:
            raise ValidationFailed("Local delivery plan not found for order change.")

        updated_old_stops, updated_old_solutions = remove_orders_stops_for_local_delivery(
            [order.id for order in plan_orders],
            old_local_delivery.id,
        )
        extra_instances.extend(updated_old_stops)
        extra_instances.extend(updated_old_solutions)

    if new_plan.plan_type == "local_delivery":
        new_local_delivery = _get_local_delivery_plan_by_delivery_plan_id(ctx, new_plan.id)
        if not new_local_delivery:
            raise ValidationFailed("Local delivery plan not found for order change.")

        route_solutions = list(new_local_delivery.route_solutions or [])
        if not route_solutions:
            raise ValidationFailed("Route solution not found for local delivery plan.")

        created_stops, updated_new_solutions = build_route_solution_stops_for_order_ids(
            ctx,
            [order.id for order in changed_orders],
            route_solutions,
            skip_reason_for_optimized=ORDER_CHANGE_DELIVERY_PLAN_AFTER_OPTIMIZATION,
        )
        route_stop_instances.extend(created_stops)
        extra_instances.extend(created_stops)
        extra_instances.extend(updated_new_solutions)

    for order_instance in changed_orders:
        pending_events.append(
            {
                "order_id": order_instance.id,
                "event_name": OrderEvent.DELIVERY_PLAN_CHANGED.value,
                "payload": {
                    "old_delivery_plan_id": old_plan_by_order_id.get(order_instance.id),
                    "new_delivery_plan_id": new_plan.id,
                    "new_plan_type": new_plan.plan_type,
                },
                "team_id": order_instance.team_id,
            }
        )

    if extra_instances:
        db.session.add_all(extra_instances)

    db.session.flush()

    return {
        "order_ids": [order.id for order in changed_orders],
        "route_stop_instances": route_stop_instances,
        "pending_events": pending_events,
    }


def update_orders_delivery_plan(
    ctx: ServiceContext,
    order_ids: list[int | str],
    plan_id: int | str,
):
    outcome = apply_orders_delivery_plan_change(ctx, order_ids, plan_id)

    route_stop_results = (
        build_create_result(
            ctx,
            outcome["route_stop_instances"],
            extract_fields=[
                "id",
                "client_id",
                "route_solution_id",
                "order_id",
                "stop_order",
                "reason_was_skipped",
                "eta_status",
            ],
        )
        if outcome["route_stop_instances"]
        else None
    )

    db.session.commit()
    if outcome["pending_events"]:
        emit_order_events(ctx, outcome["pending_events"])

    result = {"order": outcome["order_ids"]}
    if route_stop_results is not None:
        result["order_stop"] = route_stop_results

    return result


def update_order_delivery_plan(
    ctx: ServiceContext,
    order_id: int | str,
    plan_id: int | str,
):
    outcome = update_orders_delivery_plan(ctx, [order_id], plan_id)
    result = {"order": order_id}
    if outcome.get("order_stop") is not None:
        result["order_stop"] = outcome["order_stop"]
    return result


def _get_local_delivery_plan_by_delivery_plan_id(
    ctx: ServiceContext,
    delivery_plan_id: int,
) -> LocalDeliveryPlan | None:
    query = db.session.query(LocalDeliveryPlan).filter(
        LocalDeliveryPlan.delivery_plan_id == delivery_plan_id
    )
    if ctx.team_id:
        query = query.filter(LocalDeliveryPlan.team_id == ctx.team_id)
    return query.one_or_none()
