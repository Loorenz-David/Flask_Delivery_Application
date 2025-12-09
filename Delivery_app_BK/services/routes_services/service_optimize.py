from Delivery_app_BK.models import db, Route
from Delivery_app_BK.models.managers.object_route_optimizer import (
    ObjectRouteOptimizer,
)
from Delivery_app_BK.models.managers.object_searcher import GetObject



def service_optimize_route(response, identity=None):
    """
    Orchestrates the optimization flow by delegating to ObjectRouteOptimizer.
    """
    optimizer = ObjectRouteOptimizer(response=response, identity=identity)
    optimizer.optimize_route()
    return optimizer


def service_change_optimization_indx(response, identity=None):
    data = response.incoming_data or {}
    route_id = data.get("route_id")
    using_index = data.get("using_optimization_indx")

    try:
        route_id = int(route_id)
        using_index = int(using_index)
    except (TypeError, ValueError):
        response.set_error("route_id and using_optimization_indx must be integers", status=400)
        return None

    route = GetObject.get_object(Route, route_id, identity=identity)
    if not route:
        response.set_error("Route not found", status=404)
        return None

    saved_optimizations = _normalize_saved_optimizations(route.saved_optimizations)
    if not saved_optimizations or using_index < 0 or using_index >= len(saved_optimizations):
        response.set_error("Invalid optimization index", status=400)
        return None

    selected = saved_optimizations[using_index]

    route.using_optimization_indx = using_index
    _update_route_from_optimization(route, selected)
    _update_orders_from_sequence(route, selected.get("order_sequence"))

    db.session.add(route)
    db.session.add_all(route.delivery_orders or [])
    db.session.commit()

    response.set_message("Optimization index updated.")
    response.set_payload({
        "route": _serialize_route(route),
    })
    return route


def _normalize_saved_optimizations(saved):
    if not saved:
        return []
    if isinstance(saved, list):
        return saved
    return [saved]


def _update_route_from_optimization(route, optimization):
    fields = [
        "expected_start_time",
        "expected_end_time",
        "set_start_time",
        "set_end_time",
        "start_location",
        "end_location",
        "total_distance_meters",
        "total_duration_seconds",
    ]
    for field in fields:
        value = optimization.get(field)
        if value is not None:
            setattr(route, field, value)


def _update_orders_from_sequence(route, sequence):
    orders = list(route.delivery_orders or [])
    if not orders:
        return
    order_map = {order.id: order for order in orders}
    processed_ids = set()
    max_arrangement = -1

    def apply_to_order(order_id, entry, fallback_arrangement=None):
        nonlocal max_arrangement
        order = order_map.get(order_id)
        if not order:
            return
        processed_ids.add(order_id)
        if isinstance(entry, dict):
            arrangement = entry.get("delivery_arrangement")
            expected_time = entry.get("expected_arrival_time")
        else:
            arrangement = fallback_arrangement
            expected_time = None
        if arrangement is None:
            arrangement = fallback_arrangement
        if arrangement is None:
            arrangement = order.delivery_arrangement or 0
        order.delivery_arrangement = arrangement
        max_arrangement = max(max_arrangement, arrangement)
        order.expected_arrival_time = expected_time

    if isinstance(sequence, dict):
        for key, value in sequence.items():
            try:
                order_id = int(key)
            except (TypeError, ValueError):
                continue
            apply_to_order(order_id, value)
    elif isinstance(sequence, list):
        for idx, value in enumerate(sequence):
            if isinstance(value, dict) and "order_id" in value:
                order_id = value.get("order_id")
            else:
                order_id = value
            try:
                order_id = int(order_id)
            except (TypeError, ValueError):
                continue
            apply_to_order(order_id, value if isinstance(value, dict) else None, fallback_arrangement=idx)

    next_arrangement = max_arrangement + 1 if max_arrangement >= 0 else 0
    for order in orders:
        if order.id in processed_ids:
            continue
        order.delivery_arrangement = next_arrangement
        order.expected_arrival_time = None
        next_arrangement += 1


def _serialize_route(route):
    return {
        "id": route.id,
        "route_label": route.route_label,
        "expected_start_time": route.expected_start_time,
        "expected_end_time": route.expected_end_time,
        "set_start_time": route.set_start_time,
        "set_end_time": route.set_end_time,
        "start_location": route.start_location,
        "end_location": route.end_location,
        "using_optimization_indx": route.using_optimization_indx,
        "saved_optimizations": route.saved_optimizations,
        "delivery_orders": [
            {
                "id": order.id,
                "delivery_arrangement": order.delivery_arrangement,
                "expected_arrival_time": order.expected_arrival_time,
            }
            for order in (route.delivery_orders or [])
        ],
    }
