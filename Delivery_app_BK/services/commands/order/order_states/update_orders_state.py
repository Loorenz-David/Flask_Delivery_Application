from typing import List

from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound

from Delivery_app_BK.errors import NotFound, ValidationFailed
from Delivery_app_BK.models import Order, OrderState, db
from Delivery_app_BK.services.infra.events.builders.order import (
    build_order_state_transition_events,
)
from Delivery_app_BK.services.infra.events.emiters.order import emit_order_events
from Delivery_app_BK.services.utils import (
    ensure_instance_in_team,
    model_requires_team,
    require_team_id,
)

from ....context import ServiceContext
from ....queries.get_instance import get_instance




def update_orders_state(
    ctx: ServiceContext,
    orders: int | List[int] | List[Order],
    state_id: int,
):
    if isinstance(state_id, bool) or not isinstance(state_id, int):
        raise ValidationFailed("state_id must be an integer.")

    changed_orders: list[Order] = []
    pending_events: list[dict] = []

    def _apply() -> list[Order]:
        try:
            state_instance: OrderState = get_instance(ctx, OrderState, state_id)
        except NoResultFound as exc:
            raise NotFound(str(exc)) from exc

        order_instances: list[Order] = _resolve_orders(ctx, orders)
        if not order_instances:
            return []

        changed_orders.clear()
        pending_events.clear()
        for order_instance in order_instances:
            old_state_id = order_instance.order_state_id
            if old_state_id == state_instance.id:
                continue

            order_instance.order_state_id = state_instance.id
            changed_orders.append(order_instance)
            pending_events.extend(
                build_order_state_transition_events(
                    order_instance=order_instance,
                    old_state_id=old_state_id,
                    state_instance=state_instance,
                )
            )

        return changed_orders

    try:
        with db.session.begin():
            changed_orders_result = _apply()
    except InvalidRequestError as exc:
        if "already begun" not in str(exc).lower():
            raise
        changed_orders_result = _apply()

    if pending_events:
        emit_order_events(ctx, pending_events)

    return changed_orders_result



def _resolve_orders(
    ctx: ServiceContext,
    orders: int | List[int] | List[Order],
) -> list[Order]:
    if isinstance(orders, int) and not isinstance(orders, bool):
        try:
            return [get_instance(ctx, Order, orders)]
        except NoResultFound as exc:
            raise NotFound(str(exc)) from exc

    if not isinstance(orders, list):
        raise ValidationFailed("orders must be an integer, a list of integers, or a list of Order instances.")

    if not orders:
        return []

    if all(isinstance(order_id, int) and not isinstance(order_id, bool) for order_id in orders):
        return _resolve_orders_by_ids(ctx, orders)

    if all(isinstance(order, Order) for order in orders):
        return _resolve_order_instances(ctx, orders)

    raise ValidationFailed("orders must contain only integers or only Order instances.")



def _resolve_orders_by_ids(ctx: ServiceContext, order_ids: list[int]) -> list[Order]:
    deduped_ids = list(dict.fromkeys(order_ids))
    query = db.session.query(Order).filter(Order.id.in_(deduped_ids)).with_for_update()
    if model_requires_team(Order) and ctx.check_team_id:
        query = query.filter(Order.team_id == require_team_id(ctx))

    orders = query.all()
    orders_by_id = {order.id: order for order in orders}
    missing_ids = [order_id for order_id in deduped_ids if order_id not in orders_by_id]
    if missing_ids:
        raise NotFound(f"Orders not found: {missing_ids}")

    return [orders_by_id[order_id] for order_id in deduped_ids]


def _resolve_order_instances(ctx: ServiceContext, orders: list[Order]) -> list[Order]:
    deduped_orders: list[Order] = []
    seen_ids: set[int] = set()
    for order in orders:
        if model_requires_team(Order) and ctx.check_team_id:
            ensure_instance_in_team(order, ctx)

        if order.id in seen_ids:
            continue
        seen_ids.add(order.id)
        deduped_orders.append(order)

    return deduped_orders
