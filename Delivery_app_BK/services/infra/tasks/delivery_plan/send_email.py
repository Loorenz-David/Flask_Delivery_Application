from __future__ import annotations

from Delivery_app_BK.models import DeliveryPlanEventAction, OrderEvent, OrderEventAction, db
from Delivery_app_BK.services.domain.order.order_events import OrderEvent as OrderDomainEvent

from Delivery_app_BK.services.infra.messaging import MessageRenderContext
from Delivery_app_BK.services.infra.messaging.email_service import send_email_batch


ORDER_EMAIL_ACTION_NAME = "plan_delivery_rescheduled_email"


def _truncate_error(error_message: str) -> str:
    if len(error_message) <= 3000:
        return error_message
    return error_message[:3000]


def _mark_action_failed(action: DeliveryPlanEventAction, error_message: str) -> None:
    action.status = DeliveryPlanEventAction.STATUS_FAILED
    action.last_error = _truncate_error(error_message)
    db.session.commit()


def _mark_action_success(action: DeliveryPlanEventAction) -> None:
    action.status = DeliveryPlanEventAction.STATUS_SUCCESS
    action.last_error = None
    db.session.commit()


def _create_order_events_with_actions(
    *,
    action: DeliveryPlanEventAction,
    orders: list,
    team_id: int,
    order_errors: dict[int, str],
) -> None:
    if not orders:
        return
    from Delivery_app_BK.services.infra.events import get_event_bus
    actor_id = getattr(action.event, "actor_id", None) if action.event is not None else None
    payload = {
        "source_delivery_plan_event_id": action.event_id,
    }

    event_rows: list[OrderEvent] = []
    action_rows: list[OrderEventAction] = []
    for order in orders:
        order_id = getattr(order, "id", None)
        if order_id is None:
            continue
        row = OrderEvent(
            order_id=order_id,
            event_name=OrderDomainEvent.DELIVERY_RESCHEDULED.value,
            payload=payload,
            actor_id=actor_id,
            team_id=team_id,
        )
        db.session.add(row)
        event_rows.append(row)

    if not event_rows:
        return

    db.session.flush()

    for event_row in event_rows:
        error = order_errors.get(event_row.order_id)
        is_failed = bool(error)
        action_rows.append(
            OrderEventAction(
                event_id=event_row.id,
                action_name=ORDER_EMAIL_ACTION_NAME,
                team_id=team_id,
                status=OrderEventAction.STATUS_FAILED if is_failed else OrderEventAction.STATUS_SUCCESS,
                attempts=1,
                last_error=_truncate_error(error) if is_failed else None,
            )
        )

    if action_rows:
        db.session.add_all(action_rows)

    db.session.commit()

    event_bus = get_event_bus()
    for row in event_rows:
        event_bus.publish(row)


def send_email(action_id: int) -> None:
    action = db.session.get(DeliveryPlanEventAction, action_id)
    if action is None:
        return
    if action.status == DeliveryPlanEventAction.STATUS_SUCCESS:
        return

    action.attempts = (action.attempts or 0) + 1
    db.session.commit()

    try:
        if action.event is None:
            _mark_action_failed(action, "Delivery plan event context is missing")
            return

        delivery_plan = getattr(action.event, "delivery_plan", None) or getattr(action.event, "plan", None)
        if delivery_plan is None:
            _mark_action_failed(action, "Delivery plan is missing on event context")
            return

        team_id = action.team_id if action.team_id is not None else getattr(action.event, "team_id", None)
        if team_id is None:
            _mark_action_failed(action, "Missing team context for delivery plan email send")
            return

        orders = list(getattr(delivery_plan, "orders", None) or [])
        recipients: list[tuple[int, str, MessageRenderContext]] = []
        order_errors: dict[int, str] = {}
        for order in orders:
            order_id = getattr(order, "id", None)
            if order_id is None:
                continue
            recipient = (getattr(order, "client_email", None) or "").strip()
            if not recipient:
                order_errors[order_id] = "Order has no client email"
                continue
            render_context = MessageRenderContext(
                order=order,
                delivery_plan_event=action.event,
                team_id=team_id,
            )
            recipients.append((order_id, recipient, render_context))

        send_errors = send_email_batch(
            team_id=team_id,
            recipients=recipients,
            event_name=action.event.event_name,
        )
        order_errors.update(send_errors)

        _create_order_events_with_actions(
            action=action,
            orders=orders,
            team_id=team_id,
            order_errors=order_errors,
        )

        if order_errors:
            _mark_action_failed(action, f"Failed orders: {order_errors}")
            return

        _mark_action_success(action)
    except Exception as exc:
        _mark_action_failed(action, str(exc))
