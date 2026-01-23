from typing import List
from Delivery_app_BK.models import Vehicle

from ....context import ServiceContext
from ...utils import map_return_values


def serialize_vehicles(instances: List[Vehicle], ctx: ServiceContext):
    unpacked_instances = []

    for instance in instances:
        unpacked = {
            "id": instance.id,
            "client_id": instance.client_id,
            "name": instance.name,
            "icon": instance.icon,
            "travel_mode": instance.travel_mode,
            "cost_per_hour": instance.cost_per_hour,
            "cost_per_kilometer": instance.cost_per_kilometer,
            "travel_duration_limit": instance.travel_duration_limit,
            "route_distance_limit": instance.route_distance_limit,
            "user_id": instance.user_id,
            "max_load": instance.max_load,
            "min_load": instance.min_load,
            "is_system": instance.is_system,
        }
        unpacked_instances.append(unpacked)

    return map_return_values(unpacked_instances, ctx, "vehicle")
