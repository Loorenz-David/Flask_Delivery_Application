from ..item_routers.items_default_data_request import ITEM_REQUESTED_DATA 

ORDER_REQUESTED_DATA = [
    'id',
    "client_first_name",
    "client_last_name",
    "client_primary_phone",
    "client_secondary_phone",
    "client_email",
    'client_address',
    'client_language',
    'notes_chat',
    'expected_arrival_time',
    'actual_arrival_time',
    'delivery_after',
    'delivery_before',
    'stop_time',
    'in_range',
    'delivery_arrangement',
    'route_id',
    'marketing_messages',
    'creation_date',
    {
        'delivery_items': ITEM_REQUESTED_DATA 
    },
]
