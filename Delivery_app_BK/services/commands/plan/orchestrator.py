from Delivery_app_BK.services.commands.plan.local_delivery.update_settings import (
    update_local_delivery_settings,
)
from Delivery_app_BK.services.context import ServiceContext


def update_local_delivery_plan_settings(ctx: ServiceContext):
    return update_local_delivery_settings(ctx)
