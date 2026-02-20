from __future__ import annotations

from Delivery_app_BK.models import OrderEventAction, db
from Delivery_app_BK.services.infra.messaging import MessageRenderContext
from Delivery_app_BK.services.infra.messaging.email_service import send_email_message


def _truncate_error(error_message: str) -> str:
    if len(error_message) <= 3000:
        return error_message
    return error_message[:3000]


def _mark_action_failed(action: OrderEventAction, error_message: str) -> None:
    action.status = OrderEventAction.STATUS_FAILED
    action.last_error = _truncate_error(error_message)
    db.session.commit()


def _mark_action_success(action: OrderEventAction) -> None:
    action.status = OrderEventAction.STATUS_SUCCESS
    action.last_error = None
    db.session.commit()


# Synchronous for now. This can be wrapped by Celery workers later.
def send_email(action_id: int) -> None:
    action = db.session.get(OrderEventAction, action_id)
    if action is None:
        return
    if action.status == OrderEventAction.STATUS_SUCCESS:
        return

    action.attempts = (action.attempts or 0) + 1
    db.session.commit()

    try:
        if action.event is None or action.event.order is None:
            _mark_action_failed(action, "Order event context is missing")
            return

        team_id = action.team_id if action.team_id is not None else getattr(action.event, "team_id", None)
        if team_id is None:
            _mark_action_failed(action, "Missing team context for email send")
            return

        order = action.event.order
        recipient = (order.client_email or "").strip()
        if not recipient:
            _mark_action_failed(action, "Order has no client email")
            return

        render_context = MessageRenderContext(
            order=order,
            order_event=action.event,
            team_id=team_id,
        )

        send_email_message(
            team_id=team_id,
            recipient=recipient,
            event_name=action.event.event_name,
            render_context=render_context,
        )
        _mark_action_success(action)
    except Exception as exc:
        _mark_action_failed(action, str(exc))

