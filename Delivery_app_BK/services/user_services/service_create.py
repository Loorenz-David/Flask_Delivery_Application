from Delivery_app_BK.models.tables.users_models import Team, User, UserRole, UserWarehouse, UserVehicle, RoleRules
from Delivery_app_BK.models.tables.items_models import Item
from Delivery_app_BK.services.general_services.general_creation import create_general_object


def service_create_user(fields: dict, identity=None, skip_team_check=False) -> dict:
    rel_map = {
        "team_id": Team,
        "team": Team,
        "role_id": UserRole,
    }
    processed_fields = dict(fields)
    if password := processed_fields.get("password"):
        processed_fields["password"] = User().hash_password(password)
    return create_general_object(processed_fields, User, rel_map, identity=identity, skip_team_check=skip_team_check)


def service_create_team(fields: dict, identity=None) -> dict:
    return create_general_object(fields, Team)


def service_create_user_role(fields: dict, identity=None) -> dict:
    rel_map = {
        "team_id": Team,
        "team": Team,
    }
    return create_general_object(fields, UserRole, rel_map, identity=identity)


def service_create_user_warehouse(fields: dict, identity=None) -> dict:
    rel_map = {
        "team_id": Team,
        "team": Team,
        "delivery_items": Item,
    }
    return create_general_object(fields, UserWarehouse, rel_map, identity=identity)


def service_create_user_vehicle(fields: dict, identity=None) -> dict:
    rel_map = {
        "team_id": Team,
        "team": Team,
    }
    return create_general_object(fields, UserVehicle, rel_map, identity=identity)


def service_create_role_rule(fields: dict, identity=None) -> dict:
    rel_map = {
        "team_id": Team,
        "team": Team,
        "role_id": UserRole,
        "role": UserRole,
    }
    return create_general_object(fields, RoleRules, rel_map, identity=identity)
