from sqlalchemy.orm import joinedload

from Delivery_app_BK.models import ItemCategory
from Delivery_app_BK.models.managers.object_searcher import ObjectSearcher
from Delivery_app_BK.routers.item_routers.items_default_data_request import ITEM_OPTIONS_REQUESTED_DATA
from Delivery_app_BK.services.utils import model_requires_team, require_team_id


def service_query_item_options(request_payload: dict, identity=None):
    requested_data = request_payload.get('requested_data') or ITEM_OPTIONS_REQUESTED_DATA
    order_by = request_payload.get('order_by')
    pagination = request_payload.get('pagination')
    query_filters = dict(request_payload.get('query', {}))

    if model_requires_team(ItemCategory):
        team_id = require_team_id(identity)
        query_filters.setdefault('team_id', {'operation': '==', 'value': team_id})

    searcher = ObjectSearcher(
        Obj=ItemCategory,
        query_filters=query_filters,
        requested_data=requested_data,
    )

    searcher.build_query()
    if order_by:
        searcher.order_by(order_by)
    if pagination:
        searcher.paginate(pagination)
    else:
        searcher.trigger_query()
    searcher.unpack(requested_data)
    return searcher.unpacked_data
