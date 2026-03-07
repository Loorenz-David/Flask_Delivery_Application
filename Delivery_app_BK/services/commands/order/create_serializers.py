from Delivery_app_BK.models import Item, Order, RouteSolutionStop
from Delivery_app_BK.services.domain.order.order_case_states import OrderCaseState
from Delivery_app_BK.services.domain.order.delivery_windows import (
    sort_delivery_window_instances,
)
from Delivery_app_BK.services.queries.utils import calculate_order_metrics


def serialize_created_order(instance: Order) -> dict:
    creation_date = instance.creation_date
    earliest_delivery_date = instance.earliest_delivery_date
    latest_delivery_date = instance.latest_delivery_date
    archive_at = instance.archive_at
    metrics = calculate_order_metrics(instance)
    delivery_windows = sort_delivery_window_instances(
        list(getattr(instance, "delivery_windows", None) or []),
    )

    return {
        "id": instance.id,
        "client_id": instance.client_id,
        "order_plan_objective": instance.order_plan_objective,
        "operation_type": instance.operation_type,
        "reference_number": instance.reference_number,
        "external_order_id": instance.external_order_id,
        "external_source": instance.external_source,
        "tracking_number": instance.tracking_number,
        "tracking_link": instance.tracking_link,
        "client_first_name": instance.client_first_name,
        "client_last_name": instance.client_last_name,
        "client_email": instance.client_email,
        "client_primary_phone": instance.client_primary_phone,
        "client_secondary_phone": instance.client_secondary_phone,
        "client_address": instance.client_address,
        "marketing_messages": instance.marketing_messages,
        "earliest_delivery_date": earliest_delivery_date.isoformat()
        if earliest_delivery_date
        else None,
        "latest_delivery_date": latest_delivery_date.isoformat()
        if latest_delivery_date
        else None,
        "preferred_time_start": instance.preferred_time_start,
        "preferred_time_end": instance.preferred_time_end,
        "creation_date": creation_date.isoformat() if creation_date else None,
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
        "archive_at": archive_at.isoformat() if archive_at else None,
        **metrics,
    }


def serialize_created_items(instances: list[Item]) -> list[dict]:
    return [
        {
            "id": instance.id,
            "client_id": instance.client_id,
            "article_number": instance.article_number,
            "reference_number": instance.reference_number,
            "item_type": instance.item_type,
            "item_state_id": instance.item_state_id,
            "item_position_id": instance.item_position_id,
            "order_id": instance.order_id,
            "properties": instance.properties,
            "page_link": instance.page_link,
            "dimension_depth": instance.dimension_depth,
            "dimension_height": instance.dimension_height,
            "dimension_width": instance.dimension_width,
            "weight": instance.weight,
            "quantity": instance.quantity,
        }
        for instance in instances
    ]


def serialize_created_order_stops(instances: list[RouteSolutionStop]) -> list[dict]:
    return [
        {
            "id": instance.id,
            "client_id": instance.client_id,
            "route_solution_id": instance.route_solution_id,
            "order_id": instance.order_id,
            "service_duration": instance.service_duration,
            "service_time": instance.service_time,
            "in_range": instance.in_range,
            "stop_order": instance.stop_order,
            "reason_was_skipped": instance.reason_was_skipped,
            "has_constraint_violation": instance.has_constraint_violation,
            "constraint_warnings": instance.constraint_warnings,
            "eta_status": instance.eta_status,
            "expected_arrival_time": instance.expected_arrival_time.isoformat()
            if instance.expected_arrival_time
            else None,
            "actual_arrival_time": instance.actual_arrival_time.isoformat()
            if instance.actual_arrival_time
            else None,
            "to_next_polyline": instance.to_next_polyline,
        }
        for instance in instances
    ]


def _count_open_order_cases(order: Order) -> int:
    cases = getattr(order, "order_cases", None) or []
    return sum(1 for case in cases if case.state != OrderCaseState.RESOLVED.value)
