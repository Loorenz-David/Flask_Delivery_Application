# Local Imports
from Delivery_app_BK.models import Route
from Delivery_app_BK.services.general_services.general_creation import create_general_object


from Delivery_app_BK.debug_logger import logger

"""
this functions call create_general_object for simple column fill
or simple link between relationships, if something more fancy is required
it can me modified on the service function
"""

# CREATE Route Instance 
def service_create_route(fields:dict, identity=None)->dict:
    return create_general_object(fields,Route, identity=identity)
