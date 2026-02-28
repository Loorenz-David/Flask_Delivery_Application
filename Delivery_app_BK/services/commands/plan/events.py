from typing import Iterable

from Delivery_app_BK.services.infra.events.emiters.delivery_plan import (
    emit_delivery_plan_events,
)
from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.infra.events.builders.delivery_plan import (
    build_delivery_plan_rescheduled_event,
)


def emit_pending_delivery_plan_events(
    ctx: ServiceContext,
    pending_events: Iterable[dict],
) -> None:
    events = list(pending_events)
    if not events:
        return
    emit_delivery_plan_events(ctx, events)
