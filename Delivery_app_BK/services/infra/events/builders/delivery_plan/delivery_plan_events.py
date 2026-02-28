from datetime import datetime

from Delivery_app_BK.services.domain.plan.plan_events import DeliveryPlanEvent


def build_delivery_plan_rescheduled_event(
    delivery_plan_id: int,
    old_start_date: datetime | None,
    old_end_date: datetime | None,
    new_start_date: datetime | None,
    new_end_date: datetime | None,
) -> dict:
    return {
        "delivery_plan_id": delivery_plan_id,
        "event_name": DeliveryPlanEvent.DELIVERY_PLAN_RESCHEDULED.value,
        "payload": {
            "old_start_date": old_start_date.isoformat() if old_start_date else None,
            "old_end_date": old_end_date.isoformat() if old_end_date else None,
            "new_start_date": new_start_date.isoformat() if new_start_date else None,
            "new_end_date": new_end_date.isoformat() if new_end_date else None,
        },
    }
