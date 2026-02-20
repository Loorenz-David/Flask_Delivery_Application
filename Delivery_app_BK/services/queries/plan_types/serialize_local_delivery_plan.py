from Delivery_app_BK.models import LocalDeliveryPlan 
from ...context import ServiceContext
from ..utils import map_return_values


def serialize_local_delivery_plan(instance: LocalDeliveryPlan, ctx: ServiceContext):
    unpacked_instances = [{
        "id": instance.id,
        "client_id": instance.client_id,
        "actual_start_time": instance.actual_start_time,
        "actual_end_time": instance.actual_end_time,
        "driver_id": instance.driver_id,
        "delivery_plan_id": instance.delivery_plan_id,
    }]
    mapped_instances = map_return_values(unpacked_instances, ctx, "local_delivery_plan")
    return mapped_instances[0] if isinstance(mapped_instances, list) else mapped_instances
