from typing import List
from Delivery_app_BK.models import LabelTemplate

from ....context import ServiceContext
from ...utils import map_return_values


def serialize_label_templates(instances: List[LabelTemplate], ctx: ServiceContext):
    unpacked_instances = []

    for instance in instances:
        timestampt = instance.timestampt
        unpacked = {
            "id": instance.id,
            "client_id": instance.client_id,
            "name": instance.name,
            "template_string": instance.template_string,
            "template_target": instance.template_target,
            "timestampt": timestampt.isoformat() if timestampt else None,
            "is_system": instance.is_system,
        }
        unpacked_instances.append(unpacked)

    return map_return_values(unpacked_instances, ctx, "label_template")
