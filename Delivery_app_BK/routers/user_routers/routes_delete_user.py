from flask import request
from flask_jwt_extended import jwt_required, get_jwt
from Delivery_app_BK.routers.utils.role_decorator import role_required

from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.services import (
    service_delete_user,
    service_delete_team,
    service_delete_user_role,
    service_delete_user_warehouse,
)
from . import user_bp


@user_bp.route("/delete_user", methods=["DELETE"])
@jwt_required()
@role_required([1])
def delete_user():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    # ObjectFiller.fill_object(
    #     fill_function=service_delete_user,
    #     response=response,
    #     reference="User",
    #     add_to_session=False,
    #     action_type='delete',
    # )
    return response.build()


@user_bp.route("/delete_team", methods=["DELETE"])
@jwt_required()
@role_required([1])
def delete_team():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    # ObjectFiller.fill_object(
    #     fill_function=service_delete_team,
    #     response=response,
    #     reference="Team",
    #     add_to_session=False,
    #     action_type='delete',
    # )
    return response.build()


@user_bp.route("/delete_user_role", methods=["DELETE"])
@jwt_required()
@role_required([1])
def delete_user_role():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    # ObjectFiller.fill_object(
    #     fill_function=service_delete_user_role,
    #     response=response,
    #     reference="User Role",
    #     add_to_session=False,
    #     action_type='delete',
    # )
    return response.build()


@user_bp.route("/delete_user_warehouse", methods=["DELETE"])
@jwt_required()
@role_required([1])
def delete_user_warehouse():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_delete_user_warehouse,
        response=response,
        reference="User Warehouse",
        add_to_session=False,
        action_type='delete',
    )
    return response.build()
