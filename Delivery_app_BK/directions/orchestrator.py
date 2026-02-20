from __future__ import annotations

from typing import Dict

from Delivery_app_BK.directions.providers.base import DirectionsProvider
from Delivery_app_BK.directions.providers.google import GoogleDirectionsProvider
from Delivery_app_BK.directions.services.refresher import apply_directions_result
from Delivery_app_BK.directions.services.request_builder import build_directions_request
from Delivery_app_BK.models import Order, RouteSolution, db


def refresh_route_solution(
    route_solution: RouteSolution,
    provider: DirectionsProvider | None = None,
    time_zone:str = None
) -> RouteSolution: 
    orders_by_id = _load_orders(route_solution)
    request = build_directions_request(route_solution, orders_by_id, time_zone=time_zone)
    provider = provider or GoogleDirectionsProvider()
    result = provider.compute(request)
    apply_directions_result(route_solution, result, orders_by_id)
    return route_solution


def _load_orders(route_solution: RouteSolution) -> Dict[int, Order]:
    order_ids = [
        stop.order_id
        for stop in (route_solution.stops or [])
        if stop.order_id is not None
    ]
    if not order_ids:
        return {}

    orders = (
        db.session.query(Order)
        .filter(Order.id.in_(order_ids))
        .all()
    )
    return {order.id: order for order in orders}
