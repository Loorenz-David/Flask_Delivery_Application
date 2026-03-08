from typing import List
from Delivery_app_BK.models import Order
from Delivery_app_BK.services.domain.order.order_case_states import OrderCaseState
from Delivery_app_BK.services.domain.order.delivery_windows import (
    sort_delivery_window_instances,
)

from ...context import ServiceContext
from ..utils import map_return_values, calculate_order_metrics


def _count_open_order_cases(order: Order) -> int:
    cases = getattr(order, "order_cases", None) or []
    return sum(1 for case in cases if case.state != OrderCaseState.RESOLVED.value)


def serialize_orders( instances: List[ Order ], ctx:ServiceContext  ):
    
    unpacked_instances = []

    for instance in instances:
        creation_date = instance.creation_date
        earliest_delivery_date = instance.earliest_delivery_date
        latest_delivery_date = instance.latest_delivery_date
        delivery_windows = sort_delivery_window_instances(
            list(getattr(instance, "delivery_windows", None) or []),
        )
        unpacked = {
            "id": instance.id,
            "client_id": instance.client_id,
            "order_plan_objective": instance.order_plan_objective,
            "operation_type": instance.operation_type,
            "order_scalar_id": instance.order_scalar_id,
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
            "items_updated_at": instance.items_updated_at.isoformat() if instance.items_updated_at else None,
            "order_state_id": instance.order_state_id,
            "delivery_plan_id": instance.delivery_plan_id,
            "costumer_id": instance.costumer_id,
            "delivery_windows": [
                {
                    "id": row.id,
                    "client_id": row.client_id,
                    "start_at": row.start_at.isoformat() if row.start_at else None,
                    "end_at": row.end_at.isoformat() if row.end_at else None,
                    "window_type": row.window_type,
                }
                for row in delivery_windows
            ],
            "open_order_cases": _count_open_order_cases(instance),
        }
        if instance.archive_at is not None:
            unpacked['archive_at'] = instance.archive_at
            
        unpacked.update(calculate_order_metrics(instance))
        unpacked_instances.append( unpacked )

        

    return map_return_values(unpacked_instances, ctx, "order")
