from Delivery_app_BK.models.tables.users_models import User, Team, UserRole, UserWarehouse
from Delivery_app_BK.services.general_services.general_deletion import delete_general_object


def service_delete_user(data: dict, identity=None) -> dict:
    return delete_general_object(data, User, identity=identity)


def service_delete_team(data: dict, identity=None) -> dict:
    return delete_general_object(data, Team, identity=identity)


def service_delete_user_role(data: dict, identity=None) -> dict:
    return delete_general_object(data, UserRole, identity=identity)


def service_delete_user_warehouse(data: dict, identity=None) -> dict:
    return delete_general_object(data, UserWarehouse, identity=identity)
