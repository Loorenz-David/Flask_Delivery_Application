from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from sqlalchemy import func

from Delivery_app_BK.models import Route, Order, db
from Delivery_app_BK.models.tables.items_models import Item
from Delivery_app_BK.models.managers.object_searcher import ObjectSearcher
from Delivery_app_BK.services.utils import model_requires_team, require_team_id
from Delivery_app_BK.routers.route_routers.routes_default_data_request import ROUTE_REQUESTED_DATA, ROUTE_PARTIAL_DATA


FULL_UNPACK_LIMIT = 10


def service_query_routes(request_payload: dict, identity: Optional[dict] = None):
    payload = dict(request_payload or {})
    order_by = payload.get('order_by') or {"column": "delivery_date", "direction": "asc"}
    pagination = payload.get('pagination')
    query_filters = dict(payload.get('query', {}))

    if model_requires_team(Route):
        team_id = require_team_id(identity)
        query_filters.setdefault('team_id', {'operation': '==', 'value': team_id})

    searcher = ObjectSearcher(Route, query_filters=query_filters)
    searcher.build_query()
    if order_by:
        searcher.order_by(order_by)
    if pagination:
        searcher.paginate(pagination)
    else:
        searcher.trigger_query()

    routes: List[Route] = searcher.found_objects or []
    route_ids = [route.id for route in routes]
    stats_map = build_route_statistics(route_ids, routes)

    items: List[dict] = []
    for index, route in enumerate(routes):
        is_full = index < FULL_UNPACK_LIMIT
        requested = ROUTE_REQUESTED_DATA if is_full else ROUTE_PARTIAL_DATA
        route_data = route.to_dict(requested)
        aggregates = stats_map.get(route.id) or default_metrics()
        route_data.update(aggregates)
        route_data['is_unpack'] = is_full
        items.append(route_data)

    if pagination and searcher.paginated_query:
        payload = {
            "items": items,
            "total": searcher.paginated_query.total,
            "pages": searcher.paginated_query.pages,
            "current_page": searcher.paginated_query.page,
        }
    else:
        payload = {"items": items}
    return payload


def build_route_statistics(route_ids: List[int], routes: List[Route]) -> Dict[int, dict]:
    stats = {route_id: default_metrics() for route_id in route_ids}

    if not route_ids:
        return stats

    order_counts = (
        db.session.query(Order.route_id, func.count(Order.id))
        .filter(Order.route_id.in_(route_ids))
        .group_by(Order.route_id)
        .all()
    )
    for route_id, count in order_counts:
        stats[route_id]['total_orders'] = int(count or 0)

    item_rows = (
        db.session.query(Order.route_id, Item.weight, Item.dimensions)
        .join(Item, Item.order_id == Order.id)
        .filter(Order.route_id.in_(route_ids))
        .all()
    )
    for route_id, weight, dimensions in item_rows:
        entry = stats[route_id]
        entry['total_items'] += 1
        entry['total_weight'] += int(weight or 0)
        entry['total_volume'] += compute_volume(dimensions)

    for route in routes:
        entry = stats.get(route.id)
        if entry is None:
            continue
        distance, duration = resolve_optimization_metrics(route)
        entry['total_distance_meters'] = distance
        entry['total_duration_seconds'] = duration

    return stats


def resolve_optimization_metrics(route: Route) -> Tuple[int, int]:
    saved = route.saved_optimizations or []
    indx = route.using_optimization_indx
    target = None

    if isinstance(saved, list) and saved:
        if isinstance(indx, int) and 0 <= indx < len(saved):
            target = saved[indx]
        else:
            target = saved[-1]
    elif isinstance(saved, dict):
        target = saved

    if isinstance(target, dict):
        dist = int(target.get('total_distance_meters') or 0)
        duration = int(target.get('total_duration_seconds') or 0)
        return dist, duration

    return 0, 0


def compute_volume(dimensions: Optional[dict]) -> int:
    if not isinstance(dimensions, dict):
        return 0
    depth_cm = to_positive_int(dimensions.get('depth'))
    width_cm = to_positive_int(dimensions.get('width'))
    height_cm = to_positive_int(dimensions.get('height'))
    return depth_cm * width_cm * height_cm


def to_positive_int(value) -> int:
    try:
        number = int(value)
        if number < 0:
            return 0
        return number
    except (TypeError, ValueError):
        return 0


def default_metrics() -> dict:
    return {
        'total_orders': 0,
        'total_items': 0,
        'total_weight': 0,
        'total_volume': 0,
        'total_distance_meters': 0,
        'total_duration_seconds': 0,
    }
