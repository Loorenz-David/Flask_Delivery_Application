from typing import List
from Delivery_app_BK.models import MessageTemplate

from ....context import ServiceContext
from ...utils import map_return_values


def serialize_message_templates(instances: List[MessageTemplate], ctx: ServiceContext):
    unpacked_instances = []

    for instance in instances:
        timestampt = instance.timestampt
        unpacked = {
            "id": instance.id,
            "client_id": instance.client_id,
            "content": instance.content,
            "name": instance.name,
            "channel": instance.channel,
            "timestampt": timestampt.isoformat() if timestampt else None,
            "is_system": instance.is_system,

        }
        unpacked_instances.append(unpacked)

    return map_return_values(unpacked_instances, ctx, "message_template")
