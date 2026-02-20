from datetime import datetime, timezone

from Delivery_app_BK.models import db, OrderEventAction, OrderEvent


def _upsert_action(order_event_id: int, action_name: str, team_id: int | None) -> OrderEventAction:
    action = (
        db.session.query(OrderEventAction)
        .filter(
            OrderEventAction.event_id == order_event_id,
            OrderEventAction.action_name == action_name,
        )
        .first()
    )

    if action is None:
        action = OrderEventAction(
            event_id=order_event_id,
            action_name=action_name,
            team_id=team_id,
            status=OrderEventAction.STATUS_PENDING,
            attempts=0,
            last_error=None,
        )
        db.session.add(action)
        db.session.flush()
        return action

    action.status = OrderEventAction.STATUS_PENDING
    action.updated_at = datetime.now(timezone.utc)
    db.session.flush()
    return action


def run_action(order_event, action_name: str, runner) -> None:
    team_id = getattr(order_event, "team_id", None)
    action = _upsert_action(order_event.id, action_name, team_id)
    db.session.commit()

    try:
        runner(action.id)
    except Exception as exc:
        failed_action = db.session.get(OrderEventAction, action.id)
        if failed_action is None:
            return
        failed_action.attempts = (failed_action.attempts or 0) + 1
        failed_action.status = OrderEventAction.STATUS_FAILED
        failed_action.last_error = str(exc)
        db.session.commit()
