from typing import Dict, Any

from Delivery_app_BK.models.tables.users_models import Team, User, UserRole, UserWarehouse
from Delivery_app_BK.models.tables.items_models import Item
from Delivery_app_BK.models.managers.object_searcher import GetObject
from Delivery_app_BK.models.managers.object_inspector import ColumnInspector
from Delivery_app_BK.models.managers.object_validators import ValueValidator


def _update_instance(model, instance, fields: Dict[str, Any], relationship_map: Dict[str, object]) -> None:
    for field, value in fields.items():
        column = ColumnInspector(field, model)
        target_model = relationship_map.get(field)

        if target_model and (column.is_foreign_key() or column.is_relationship()):
            link = instance.update_link(
                column=column,
                value=value,
                target_model=target_model,
            )
            if not link:
                raise Exception(f"Failed to update relation '{field}' on {model.__name__}")
            continue

        column_type = column.get_python_type()
        valid_value = ValueValidator.is_valid_value(value, column_type)
        setattr(instance, column.column_name, valid_value)


def service_update_user(data: dict) -> dict:
    user = GetObject.get_object(User, data.get("id"))
    fields = data.get("fields", {})
    relationship_map = {
        "team_id": Team,
        "team": Team,
        "role": UserRole,
    }

    _update_instance(User, user, fields, relationship_map)
    return {"status": "ok", "instance": user}


def service_update_team(data: dict) -> dict:
    team = GetObject.get_object(Team, data.get("id"))
    fields = data.get("fields", {})

    _update_instance(Team, team, fields, relationship_map={})
    return {"status": "ok", "instance": team}


def service_update_user_role(data: dict) -> dict:
    user_role = GetObject.get_object(UserRole, data.get("id"))
    fields = data.get("fields", {})
    relationship_map = {
        "team_id": Team,
        "team": Team,
    }

    _update_instance(UserRole, user_role, fields, relationship_map)
    return {"status": "ok", "instance": user_role}


def service_update_user_warehouse(data: dict) -> dict:
    warehouse = GetObject.get_object(UserWarehouse, data.get("id"))
    fields = data.get("fields", {})
    relationship_map = {
        "team_id": Team,
        "team": Team,
        "delivery_items": Item,
    }

    _update_instance(UserWarehouse, warehouse, fields, relationship_map)
    return {"status": "ok", "instance": warehouse}
