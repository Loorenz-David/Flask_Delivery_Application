from typing import List
from Delivery_app_BK.models import Warehouse 

from ....context import ServiceContext
from ...utils import map_return_values


def serialize_warehouses(instances: List[ Warehouse ], ctx: ServiceContext):
    unpacked_instances = []

    for instance in instances:
        unpacked = {
            "id": instance.id,
            "client_id": instance.client_id,
            "name": instance.name,
            "property_location": instance.property_location,

        }
        unpacked_instances.append(unpacked)

    return map_return_values(unpacked_instances, ctx, "warehouse")
