
# Local Imports
from Delivery_app_BK.models import (
    db,
    Item,
    Order,
    ItemType,
    ItemCategory,
    ItemProperty,
    ItemState,
    ItemPosition,
)
from Delivery_app_BK.services import create_general_object




"""
this functions call create_general_object for simple column fill
or simple link between relationships, if something more fancy is required
it can me modified on the service function
"""

# CREATE ItemCategory Instance
def service_create_item_category(fields:dict) -> dict:
    return create_general_object(fields, ItemCategory)


# CREATE ItemType Instance
def service_create_item_type(fields:dict) -> dict:
    rel_map = {
        'properties':ItemProperty
    }

    return create_general_object(fields, ItemType,rel_map)


# CREATE ItemProperty Instance
def service_create_item_property(fields:dict) -> dict:
    rel_map = {
        'types':ItemType,
        "items":Item
    }

    return create_general_object(fields, ItemProperty,rel_map)

# CREATE ItemState Instance
def service_create_item_state(fields: dict) -> dict:
    return create_general_object(fields, ItemState)


# CREATE ItemPosition Instance
def service_create_item_position(fields: dict) -> dict:
    return create_general_object(fields, ItemPosition)

# CREATE Item Instance
def service_create_item(fields:dict) -> dict:
    rel_map = {
        'order_id':Order,
        'item_type_id':ItemType,
        'item_category_id':ItemCategory,
        'item_state_id':ItemState,
        'item_position_id':ItemPosition,
        'properties':ItemProperty
    }

    return create_general_object(fields, Item, rel_map)
