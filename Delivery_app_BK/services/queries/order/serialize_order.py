from typing import List
from Delivery_app_BK.models import Order

from ...context import ServiceContext
from ..utils import map_return_values, calculate_order_metrics


def serialize_orders( instances: List[ Order ], ctx:ServiceContext  ):
    
    unpacked_instances = []

    for instance in instances:
        creation_date = instance.creation_date
        earliest_delivery_date = instance.earliest_delivery_date
        latest_delivery_date = instance.latest_delivery_date
        unpacked = {
            "id": instance.id,
            "client_id": instance.client_id,
            "order_plan_intention": instance.order_plan_intention,
            "reference_number": instance.reference_number,
            "external_order_id": instance.external_order_id,
            "external_source": instance.external_source,
            "tracking_number": instance.tracking_number,
            "client_first_name": instance.client_first_name,
            "client_last_name": instance.client_last_name,
            "client_email": instance.client_email,
            "client_primary_phone": instance.client_primary_phone,
            "client_secondary_phone": instance.client_secondary_phone,
            "client_address": instance.client_address,
            "marketing_messages": instance.marketing_messages,
            "earliest_delivery_date": earliest_delivery_date.isoformat() if earliest_delivery_date else None,
            "latest_delivery_date": latest_delivery_date.isoformat() if latest_delivery_date else None,
            "preferred_time_start": instance.preferred_time_start,
            "preferred_time_end": instance.preferred_time_end,
            "creation_date": creation_date.isoformat() if creation_date else None,
            "order_state_id": instance.order_state_id,
            "delivery_plan_id": instance.delivery_plan_id,
        }
        unpacked.update(calculate_order_metrics(instance))
        unpacked_instances.append( unpacked )

        

    return map_return_values(unpacked_instances, ctx, "order")
