from __future__ import annotations

from typing import Any

from Delivery_app_BK.models import OrderEventAction, db
from Delivery_app_BK.services.infra.messaging import MessageRenderContext
from Delivery_app_BK.services.infra.messaging.sms_service import send_sms_message


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


# Synchronous for now. This can be wrapped by Celery workers later.
def send_sms(action_id: int) -> None:
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
            _mark_action_failed(action, "Missing team context for SMS send")
            return

        order = action.event.order
        recipient_phone = _resolve_recipient_phone(order)
        if not recipient_phone:
            _mark_action_failed(action, "Order has no valid recipient phone number")
            return

        render_context = MessageRenderContext(
            order=order,
            order_event=action.event,
            team_id=team_id,
        )

        send_sms_message(
            team_id=team_id,
            recipient_phone=recipient_phone,
            event_name=action.event.event_name,
            render_context=render_context,
        )
        _mark_action_success(action)
    except Exception as exc:
        _mark_action_failed(action, str(exc))

