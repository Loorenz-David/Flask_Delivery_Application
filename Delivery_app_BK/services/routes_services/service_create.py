# Local Imports
from Delivery_app_BK.models import Route, RouteState,Order
from Delivery_app_BK.models import User
from Delivery_app_BK.services.general_services.general_creation import create_general_object


from Delivery_app_BK.debug_logger import logger

"""
this functions call create_general_object for simple column fill
or simple link between relationships, if something more fancy is required
it can me modified on the service function
"""

# CREATE Route Instance 
def service_create_route(fields:dict, identity=None)->dict:

    rel_map = {
        'route_state':RouteState,
        'state_id':RouteState,
        "driver":User,
        "driver_id":User,
        'delivery_orders':Order
    }
    return create_general_object(fields,Route,rel_map, identity=identity)


# CREATE RouteState Instance
def service_create_route_state(fields: dict, identity=None) -> dict:
    return create_general_object(fields, RouteState, identity=identity)
