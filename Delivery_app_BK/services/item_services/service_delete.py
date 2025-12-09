from Delivery_app_BK.models.tables.items_models import (
    Item,
    ItemCategory,
    ItemType,
    ItemProperty,
    ItemState,
    ItemPosition,
)
from Delivery_app_BK.services.general_services.general_deletion import delete_general_object


def service_delete_item(data: dict, identity=None) -> dict:
    return delete_general_object(data, Item, identity=identity)


def service_delete_item_category(data: dict, identity=None) -> dict:
    return delete_general_object(data, ItemCategory, identity=identity)


def service_delete_item_type(data: dict, identity=None) -> dict:
    return delete_general_object(data, ItemType, identity=identity)


def service_delete_item_property(data: dict, identity=None) -> dict:
    return delete_general_object(data, ItemProperty, identity=identity)


def service_delete_item_state(data: dict, identity=None) -> dict:
    return delete_general_object(data, ItemState, identity=identity)


def service_delete_item_position(data: dict, identity=None) -> dict:
    return delete_general_object(data, ItemPosition, identity=identity)
