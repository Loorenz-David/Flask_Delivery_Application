from Delivery_app_BK.services.domain.plan.plan_events import DeliveryPlanEvent
from Delivery_app_BK.services.infra.events.event_bus import EventBus
from Delivery_app_BK.services.infra.events.handlers.delivery_plan.delivery_plan_email import (
    send_email_on_plan_delivery_rescheduled,
)
from Delivery_app_BK.services.infra.events.handlers.delivery_plan.delivery_plan_sms import (
    send_sms_on_plan_delivery_rescheduled,
)


def register_delivery_plan_event_handlers(event_bus: EventBus) -> None:
    event_bus.register(
        DeliveryPlanEvent.DELIVERY_PLAN_RESCHEDULED.value,
        send_sms_on_plan_delivery_rescheduled,
    )
    event_bus.register(
        DeliveryPlanEvent.DELIVERY_PLAN_RESCHEDULED.value,
        send_email_on_plan_delivery_rescheduled,
    )
