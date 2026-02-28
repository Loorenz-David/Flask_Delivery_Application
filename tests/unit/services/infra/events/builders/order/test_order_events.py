from datetime import datetime, timezone
from types import SimpleNamespace

from Delivery_app_BK.services.domain.order.order_events import OrderEvent
from Delivery_app_BK.services.infra.events.builders.order import (
    build_delivery_window_rescheduled_by_user_event,
)


def test_build_delivery_window_rescheduled_by_user_event_formats_payload():
    order = SimpleNamespace(id=7, team_id=3)
    old_earliest = datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc)
    old_latest = datetime(2026, 3, 1, 12, 0, tzinfo=timezone.utc)
    new_earliest = datetime(2026, 3, 1, 11, 0, tzinfo=timezone.utc)
    new_latest = datetime(2026, 3, 1, 13, 0, tzinfo=timezone.utc)

    event = build_delivery_window_rescheduled_by_user_event(
        order_instance=order,
        old_earliest=old_earliest,
        old_latest=old_latest,
        new_earliest=new_earliest,
        new_latest=new_latest,
    )

    assert event["order_id"] == 7
    assert event["team_id"] == 3
    assert event["event_name"] == OrderEvent.DELIVERY_WINDOW_RESCHEDULED_BY_USER.value
    assert event["payload"]["old_earliest_delivery_date"] == old_earliest.isoformat()
    assert event["payload"]["old_latest_delivery_date"] == old_latest.isoformat()
    assert event["payload"]["new_earliest_delivery_date"] == new_earliest.isoformat()
    assert event["payload"]["new_latest_delivery_date"] == new_latest.isoformat()
