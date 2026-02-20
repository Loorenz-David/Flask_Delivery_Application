from __future__ import annotations

from typing import Any

from Delivery_app_BK.models import DeliveryPlanEventAction, OrderEvent, OrderEventAction, db
from Delivery_app_BK.services.domain.order.order_events import OrderEvent as OrderDomainEvent

from Delivery_app_BK.services.infra.messaging import MessageRenderContext
from Delivery_app_BK.services.infra.messaging.sms_service import send_sms_batch


ORDER_SMS_ACTION_NAME = "plan_delivery_rescheduled_sms"


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


def _extract_phone_value(source: Any) -> str | None:
    def _normalize_phone_fragment(value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            return ""
        return "".join(ch for ch in cleaned if ch.isdigit() or ch == "+")

    def _join_prefix_and_number(prefix: str, number: str) -> str:
        normalized_prefix = _normalize_phone_fragment(prefix)
        normalized_number = _normalize_phone_fragment(number).lstrip("+")
        if not normalized_number:
            return ""
        if not normalized_prefix:
            return normalized_number
        if not normalized_prefix.startswith("+"):
            normalized_prefix = f"+{normalized_prefix.lstrip('+')}"
        return f"{normalized_prefix}{normalized_number}"

    if isinstance(source, dict):
        number_candidate = source.get("number") or source.get("phone")
        if not isinstance(number_candidate, str):
            return None

        prefix_candidate = source.get("prefix")
        if isinstance(prefix_candidate, (int, float)):
            prefix_candidate = str(int(prefix_candidate))
        if not isinstance(prefix_candidate, str):
            prefix_candidate = ""

        combined = _join_prefix_and_number(prefix_candidate, number_candidate)
        if combined:
            return combined

        source = number_candidate

    if not isinstance(source, str):
        return None

    raw_value = source.strip()
    if not raw_value:
        return None

    for separator in ("/", ",", ";"):
        if separator in raw_value:
            segments = [segment.strip() for segment in raw_value.split(separator)]
            for segment in segments:
                normalized_segment = _normalize_phone_fragment(segment)
                if normalized_segment:
                    return normalized_segment
            return None

    value = _normalize_phone_fragment(raw_value)
    if not value:
        return None
    return value


def _resolve_recipient_phone(order) -> str | None:
    primary = _extract_phone_value(getattr(order, "client_primary_phone", None))
    if primary:
        return primary

    secondary = _extract_phone_value(getattr(order, "client_secondary_phone", None))
    if secondary:
        return secondary

    return None


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
                action_name=ORDER_SMS_ACTION_NAME,
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


def send_sms(action_id: int) -> None:
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

        delivery_plan =  getattr(action.event, "delivery_plan", None) or getattr(action.event, "plan", None)
        if delivery_plan is None:
            _mark_action_failed(action, "Delivery plan is missing on event context")
            return

        team_id = action.team_id if action.team_id is not None else getattr(action.event, "team_id", None)
        if team_id is None:
            _mark_action_failed(action, "Missing team context for delivery plan SMS send")
            return

        orders = list(getattr(delivery_plan, "orders", None) or [])
        recipients: list[tuple[int, str, MessageRenderContext]] = []
        order_errors: dict[int, str] = {}
        for order in orders:
            order_id = getattr(order, "id", None)
            if order_id is None:
                continue
            recipient_phone = _resolve_recipient_phone(order)
            if not recipient_phone:
                order_errors[order_id] = "Order has no valid recipient phone number"
                continue
            render_context = MessageRenderContext(
                order=order,
                delivery_plan_event=action.event,
                team_id=team_id,
            )
            recipients.append((order_id, recipient_phone, render_context))

        send_errors = send_sms_batch(
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
