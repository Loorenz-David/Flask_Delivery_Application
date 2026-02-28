from __future__ import annotations

from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound

from Delivery_app_BK.errors import NotFound, ValidationFailed
from Delivery_app_BK.models import (
    DeliveryPlan,
    Order,
    db,
)
from Delivery_app_BK.services.infra.events.builders.order import (
    build_delivery_plan_changed_event,
)
from Delivery_app_BK.services.infra.events.emiters.order import emit_order_events
from Delivery_app_BK.services.utils import model_requires_team, require_team_id

from ...context import ServiceContext
from ...queries.get_instance import get_instance
from .create_serializers import serialize_created_order
from .plan_changes import (
    PlanChangeResult,
    apply_order_plan_change,
    build_plan_change_apply_context,
)


def apply_orders_delivery_plan_change(
    ctx: ServiceContext,
    order_ids: int | list[int],
    plan_id: int,
) -> dict:
    normalized_order_ids = _normalize_order_ids(order_ids)
    if not normalized_order_ids:
        return {
            "updated": [],
            "pending_events": [],
        }

    new_plan = _resolve_plan_instance(ctx, plan_id)
    orders_by_target_id = _resolve_orders_for_update(ctx, normalized_order_ids)

    old_plan_ids: set[int] = set()
    changed_orders: list[Order] = []
    old_plan_id_by_order_id: dict[int, int | None] = {}

    for target_id in normalized_order_ids:
        order_instance = orders_by_target_id[target_id]
        old_plan_id = order_instance.delivery_plan_id

        if old_plan_id == new_plan.id:
            ctx.set_warning(
                f"Order: {target_id}. Is already in the plan that was provided on update"
            )
            continue

        if old_plan_id is not None:
            old_plan_ids.add(old_plan_id)

        old_plan_id_by_order_id[order_instance.id] = old_plan_id
        changed_orders.append(order_instance)

    if not changed_orders:
        return {
            "updated": [],
            "pending_events": [],
        }

    old_plans_by_id = _load_delivery_plans_by_id(ctx, list(old_plan_ids))
    relevant_plan_ids = set(old_plan_ids)
    relevant_plan_ids.add(new_plan.id)
    relevant_plan_types = {new_plan.plan_type}
    relevant_plan_types.update(
        plan.plan_type
        for plan in old_plans_by_id.values()
        if getattr(plan, "plan_type", None)
    )
    apply_context = build_plan_change_apply_context(
        ctx=ctx,
        plan_ids=list(relevant_plan_ids),
        relevant_plan_types=relevant_plan_types,
    )

    pending_events: list[dict] = []
    extra_instances: list[object] = []
    post_flush_actions = []
    plan_change_result_by_order_id: dict[int, PlanChangeResult] = {}

    for target_id in normalized_order_ids:
        order_instance = orders_by_target_id[target_id]
        if order_instance.id not in old_plan_id_by_order_id:
            continue

        old_plan_id = old_plan_id_by_order_id[order_instance.id]
        old_plan = old_plans_by_id.get(old_plan_id) if old_plan_id else None

        order_instance.delivery_plan_id = new_plan.id
        order_instance.order_plan_objective = new_plan.plan_type

        change_result = apply_order_plan_change(
            ctx=ctx,
            order_instance=order_instance,
            old_plan=old_plan,
            new_plan=new_plan,
            apply_context=apply_context,
        )
        plan_change_result_by_order_id[order_instance.id] = change_result
        extra_instances.extend(change_result.instances)
        post_flush_actions.extend(change_result.post_flush_actions)

        pending_events.append(
            build_delivery_plan_changed_event(order_instance, old_plan_id, new_plan)
        )

    if extra_instances:
        db.session.add_all(extra_instances)

    db.session.flush()

    for action in post_flush_actions:
        action()
    if post_flush_actions:
        db.session.flush()

    updated_bundles: list[dict] = []
    for target_id in normalized_order_ids:
        order_instance = orders_by_target_id[target_id]
        if order_instance.id not in old_plan_id_by_order_id:
            continue

        bundle = {
            "order": serialize_created_order(order_instance),
        }
        change_result = plan_change_result_by_order_id.get(order_instance.id)
        if change_result:
            bundle.update(change_result.serialize_bundle())

        updated_bundles.append(bundle)

    return {
        "updated": updated_bundles,
        "pending_events": pending_events,
    }


def update_orders_delivery_plan(
    ctx: ServiceContext,
    order_ids: int | list[int],
    plan_id: int,
) -> dict:
    try:
        with db.session.begin():
            outcome = apply_orders_delivery_plan_change(ctx, order_ids, plan_id)
    except InvalidRequestError as exc:
        if "already begun" not in str(exc).lower():
            raise
        outcome = apply_orders_delivery_plan_change(ctx, order_ids, plan_id)

    pending_events = outcome.get("pending_events") or []
    if pending_events:
        emit_order_events(ctx, pending_events)

    return {"updated": outcome.get("updated") or []}


def update_order_delivery_plan(
    ctx: ServiceContext,
    order_id: int,
    plan_id: int,
) -> dict:
    return update_orders_delivery_plan(ctx, order_id, plan_id)



def _normalize_order_ids(order_ids: int | list[int]) -> list[int]:
    if isinstance(order_ids, int) and not isinstance(order_ids, bool):
        return [order_ids]

    if not isinstance(order_ids, list):
        raise ValidationFailed("order_ids must be provided as an integer or list.")

    deduped_order_ids: list[int] = []
    seen: set[int] = set()
    for order_id in order_ids:
        if isinstance(order_id, bool) or not isinstance(order_id, int):
            raise ValidationFailed("Each order id must be an integer.")
        if order_id in seen:
            continue
        seen.add(order_id)
        deduped_order_ids.append(order_id)

    return deduped_order_ids


def _resolve_plan_instance(ctx: ServiceContext, plan_id: int) -> DeliveryPlan:
    if isinstance(plan_id, bool) or not isinstance(plan_id, int):
        raise ValidationFailed("plan_id must be provided as an integer.")
    try:
        return get_instance(ctx, DeliveryPlan, plan_id)
    except NoResultFound as exc:
        raise NotFound(str(exc)) from exc


def _resolve_orders_for_update(
    ctx: ServiceContext,
    order_ids: list[int],
) -> dict[int, Order]:
    if not order_ids:
        return {}

    deduped_order_ids = list(dict.fromkeys(order_ids))
    orders_by_id: dict[int, Order] = {}

    team_id = None
    if model_requires_team(Order) and ctx.check_team_id:
        team_id = require_team_id(ctx)

    query = db.session.query(Order).filter(Order.id.in_(deduped_order_ids)).with_for_update()
    if team_id is not None:
        query = query.filter(Order.team_id == team_id)
    for order in query.all():
        orders_by_id[order.id] = order

    missing_ids = [order_id for order_id in deduped_order_ids if order_id not in orders_by_id]
    if missing_ids:
        raise NotFound(f"Orders not found: {missing_ids}")

    return {order_id: orders_by_id[order_id] for order_id in deduped_order_ids}


def _load_delivery_plans_by_id(
    ctx: ServiceContext,
    plan_ids: list[int],
) -> dict[int, DeliveryPlan]:
    deduped_plan_ids = list(dict.fromkeys(plan_ids))
    if not deduped_plan_ids:
        return {}

    query = db.session.query(DeliveryPlan).filter(DeliveryPlan.id.in_(deduped_plan_ids))
    if ctx.team_id:
        query = query.filter(DeliveryPlan.team_id == ctx.team_id)

    return {plan.id: plan for plan in query.all()}
