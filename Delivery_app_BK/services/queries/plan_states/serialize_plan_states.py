from typing import Type,List
from Delivery_app_BK.models import DeliveryPlanState

from ...context import ServiceContext
from ..utils import map_return_values


def serialize_plan_states(instances: List[DeliveryPlanState], ctx: ServiceContext):
    unpacked_instances = []

    for instance in instances:
        unpacked = {
            "id": instance.id,
            "client_id": instance.client_id,
            "name": instance.name,
            "index": instance.index,
            "color": instance.color,
            "is_system": instance.is_system,
        }
        unpacked_instances.append(unpacked)

    return map_return_values(unpacked_instances, ctx, "plan_state")
