from typing import List
from sqlalchemy.orm.exc import NoResultFound

from Delivery_app_BK.errors import NotFound
from Delivery_app_BK.models import db, Order, OrderState
from ...context import ServiceContext
from ...domain.order.order_events import OrderEvent
from ...queries.get_instance import get_instance
from ..order.event_emitter import emit_order_events

def resolve_orders(
    ctx:ServiceContext,
    orders: int | List[int] | List[Order], 
    state_id:int
):
    if isinstance(orders, int):
        try:
            order_instance: Order = get_instance(ctx, Order, orders)
            if order_instance.order_state_id == state_id:
                return []
            return [order_instance]
        except NoResultFound as exc:
            raise NotFound(str(exc)) from exc

    elif isinstance(orders,list) and all(isinstance(order_id, int) for order_id in orders):
        return []

    elif isinstance(orders,list) and all(isinstance(order, Order) for order in orders):
        return orders
    

def update_orders_state(
    ctx: ServiceContext,
    orders: int | List[int] | List[Order],
    state_id: int,

):
    try:
        order_instances:List[Order] = resolve_orders(ctx, orders, state_id)
        state_instance: OrderState = get_instance(ctx, OrderState, state_id)
    except NoResultFound as exc:
        raise NotFound(str(exc)) from exc
 
    changed_orders = []
    for order_instance in order_instances:
        old_state_id = order_instance.order_state_id
        order_instance.order_state_id = state_instance.id
        changed_orders.append({
            "old_state_id": old_state_id,
            "order_instance":order_instance,
        })


    db.session.commit()

    pending_events = []

    for changed_order in changed_orders:
        events_build = pending_event_builder(
            old_state_id=changed_order["old_state_id"],
            order_instance=changed_order["order_instance"],
            state_instance=state_instance
        )
        pending_events.extend(events_build)

    
    emit_order_events(ctx, pending_events)
    
    return order_instances


def pending_event_builder (old_state_id:int, order_instance:Order, state_instance:OrderState,):
    pending_events = []
    if old_state_id != state_instance.id:
        pending_events.append(
            {
                "order_id": order_instance.id,
                "event_name": OrderEvent.STATUS_CHANGED.value,
                "payload": {
                    "old_order_state_id": old_state_id,
                    "new_order_state_id": state_instance.id,
                    "new_order_state_name": state_instance.name,
                },
                "team_id": order_instance.team_id,
            }
        )

        state_name = (state_instance.name or "").strip().lower()
        if "draft" in state_name:
            pending_events.append(
                {
                    "order_id": order_instance.id,
                    "event_name": OrderEvent.CREATED.value,
                    "payload": {"order_state_id": state_instance.id},
                    "team_id": order_instance.team_id,
                }
            )
            
        elif "confirm" in state_name:
            pending_events.append(
                {
                    "order_id": order_instance.id,
                    "event_name": OrderEvent.CONFIRMED.value,
                    "payload": {"order_state_id": state_instance.id},
                    "team_id": order_instance.team_id,
                }
            )
        elif "prepar" in state_name:
            pending_events.append(
                {
                    "order_id": order_instance.id,
                    "event_name": OrderEvent.PREPARING.value,
                    "payload": {"order_state_id": state_instance.id},
                    "team_id": order_instance.team_id,
                }
            )
        elif "ready" in state_name:
            pending_events.append(
                {
                    "order_id": order_instance.id,
                    "event_name": OrderEvent.READY.value,
                    "payload": {"order_state_id": state_instance.id},
                    "team_id": order_instance.team_id,
                }
            )
        elif "processing" in state_name:
            pending_events.append(
                {
                    "order_id": order_instance.id,
                    "event_name": OrderEvent.PROCESSING.value,
                    "payload": {"order_state_id": state_instance.id},
                    "team_id": order_instance.team_id,
                }
            )
        elif "fail" in state_name:
            pending_events.append(
                {
                    "order_id": order_instance.id,
                    "event_name": OrderEvent.FAIL.value,
                    "payload": {"order_state_id": state_instance.id},
                    "team_id": order_instance.team_id,
                }
            )
        elif "cancel" in state_name:
            pending_events.append(
                {
                    "order_id": order_instance.id,
                    "event_name": OrderEvent.CANCELLED.value,
                    "payload": {"order_state_id": state_instance.id},
                    "team_id": order_instance.team_id,
                }
            )
        elif "complete" in state_name:
            pending_events.append(
                {
                    "order_id": order_instance.id,
                    "event_name": OrderEvent.COMPLETED.value,
                    "payload": {"order_state_id": state_instance.id},
                    "team_id": order_instance.team_id,
                }
            )
    return pending_events