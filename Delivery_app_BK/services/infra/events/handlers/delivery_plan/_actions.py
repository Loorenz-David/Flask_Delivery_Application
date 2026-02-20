from datetime import datetime, timezone

from Delivery_app_BK.models.tables.delivery_plan.delivery_plan_event import DeliveryPlanEvent
from Delivery_app_BK.models import db, DeliveryPlanEventAction


def _upsert_action(plan_event_id: int, action_name: str, team_id: int | None) -> DeliveryPlanEventAction:
    action = (
        db.session.query(DeliveryPlanEventAction)
        .filter(
            DeliveryPlanEventAction.event_id == plan_event_id,
            DeliveryPlanEventAction.action_name == action_name,
        )
        .first()
    )

    if action is None:
        action = DeliveryPlanEventAction(
            event_id=plan_event_id,
            action_name=action_name,
            team_id=team_id,
            status=DeliveryPlanEventAction.STATUS_PENDING,
            attempts=0,
            last_error=None,
        )
        db.session.add(action)
        db.session.flush()
        return action

    action.status = DeliveryPlanEventAction.STATUS_PENDING
    action.updated_at = datetime.now(timezone.utc)
    db.session.flush()
    return action


def run_action(plan_event:DeliveryPlanEvent, action_name: str, runner) -> None:
  
    team_id = getattr(plan_event, "team_id", None)
    action = _upsert_action(plan_event.id, action_name, team_id)
    db.session.commit()

    try:
        runner(action.id)
    except Exception as exc:
        failed_action = db.session.get(DeliveryPlanEventAction, action.id)
        if failed_action is None:
            return
        failed_action.attempts = (failed_action.attempts or 0) + 1
        failed_action.status = DeliveryPlanEventAction.STATUS_FAILED
        failed_action.last_error = str(exc)
        db.session.commit()
