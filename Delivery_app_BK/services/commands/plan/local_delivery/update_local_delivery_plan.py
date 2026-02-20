from Delivery_app_BK.models import LocalDeliveryPlan


def update_local_delivery_plan(
    local_delivery_plan: LocalDeliveryPlan,
    fields: dict | None,
) -> LocalDeliveryPlan:
    if not fields:
        return local_delivery_plan

    if "driver_id" in fields:
        local_delivery_plan.driver_id = fields.get("driver_id")

    if "actual_start_time" in fields:
        local_delivery_plan.actual_start_time = fields.get("actual_start_time")

    if "actual_end_time" in fields:
        local_delivery_plan.actual_end_time = fields.get("actual_end_time")

    return local_delivery_plan
