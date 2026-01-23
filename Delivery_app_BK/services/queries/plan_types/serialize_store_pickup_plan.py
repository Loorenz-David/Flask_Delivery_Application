from Delivery_app_BK.models import StorePickupPlan
from ...context import ServiceContext
from ..utils import map_return_values


def serialize_store_pickup_plan(instance: StorePickupPlan, ctx: ServiceContext):
    unpacked_instances = [{
        "id": instance.id,
        "client_id": instance.client_id,
        "pickup_location": instance.pickup_location,
        "assigned_user_id":instance.assigned_user_id,
        "delivery_plan_id": instance.delivery_plan_id,
    }]
    mapped_instances = map_return_values(unpacked_instances, ctx, "store_pickup_plan")
    return mapped_instances[0] if isinstance(mapped_instances, list) else mapped_instances
