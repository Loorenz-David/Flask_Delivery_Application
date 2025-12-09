from typing import Any, Dict, Optional

from Delivery_app_BK.models import Item, ItemState, ItemPosition, ItemProperty, ItemType, ItemCategory
from Delivery_app_BK.models.managers.object_searcher import GetObject
from Delivery_app_BK.models.managers.object_inspector import ColumnInspector
from Delivery_app_BK.models.managers.object_validators import ValueValidator




LinkMap = Dict[str, Dict[str, Any]]


def _update_model_with_links(Model, data: dict, identity=None, link_map: Optional[LinkMap] = None):
    obj = GetObject.get_object(Model, data.get('id'), identity=identity)
    fields: dict = data.get('fields') or {}
    if not isinstance(fields, dict):
        raise ValueError("Fields must be provided as a dictionary")

    for field, value in fields.items():
        column = ColumnInspector(field, Model)
        column_name = column.column_name

        link_config = (link_map or {}).get(column_name)
        if link_config:
            target_model = link_config.get('target_model')
            if target_model is None:
                raise ValueError(f"Missing target model for link column '{column_name}' on '{Model.__name__}'")
            link = obj.update_link(
                column=column,
                value=value,
                target_model=target_model,
                record_column=link_config.get('record_column'),
                identity=identity,
            )
            if not link:
                raise Exception(f"Something went wrong updating the column {column_name} on model {Model.__name__}")
            continue

        column_type = column.get_python_type()
        valid_value = ValueValidator.is_valid_value(value, column_type)
        setattr(obj, column_name, valid_value)

    return obj


def service_update_item(data: dict, identity=None):
    link_map = {
        'item_state_id': {'target_model': ItemState, 'record_column': 'item_state_record'},
        'item_position_id': {'target_model': ItemPosition, 'record_column': 'item_position_record'},
    }
    item_obj = _update_model_with_links(Item, data, identity=identity, link_map=link_map)
    return {'status': 'ok', 'instance': item_obj}


def service_update_item_category(data: dict, identity=None):
    link_map = {
        'item_types': {'target_model': ItemType},
    }
    item_category = _update_model_with_links(ItemCategory, data, identity=identity, link_map=link_map)
    return {'status': 'ok', 'instance': item_category}


def service_update_item_type(data: dict, identity=None):
    link_map = {
        'item_category_id': {'target_model': ItemCategory},
        'properties': {'target_model': ItemProperty},
    }
    item_type = _update_model_with_links(ItemType, data, identity=identity, link_map=link_map)
    return {'status': 'ok', 'instance': item_type}


def service_update_item_property(data: dict, identity=None):
    link_map = {
        'item_types': {'target_model': ItemType},
    }
    item_property = _update_model_with_links(ItemProperty, data, identity=identity, link_map=link_map)
    return {'status': 'ok', 'instance': item_property}


def service_update_item_state(data: dict, identity=None):
    item_state = _update_model_with_links(ItemState, data, identity=identity)
    return {'status': 'ok', 'instance': item_state}


def service_update_item_position(data: dict, identity=None):
    item_position = _update_model_with_links(ItemPosition, data, identity=identity)
    return {'status': 'ok', 'instance': item_position}
