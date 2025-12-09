from ..order_routers.orders_default_data_request import ORDER_REQUESTED_DATA

ROUTE_REQUESTED_DATA = [
    'id',
    'route_label',
    'delivery_date',
    'expected_start_time',
    'expected_end_time',
    'actual_start_time',
    'actual_end_time',
    'set_start_time',
    'set_end_time',
    'start_location',
    'end_location',
    'using_optimization_indx',
    'saved_optimizations',
    'is_optimized',
    'state_id',
    'arrival_time_range',
    'driver_id',
    {
        'delivery_orders': ORDER_REQUESTED_DATA
    },
]

ROUTE_PARTIAL_DATA = [
    'id',
    'route_label',
    'delivery_date',
    'is_optimized',
    'state_id',
    'driver_id',
]