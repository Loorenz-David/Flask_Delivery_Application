from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from . import user_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.services import (
    service_update_user,
    service_update_team,
    service_update_user_role,
    service_update_user_warehouse,
)


@user_bp.route("/update_user", methods=["PUT"])
@jwt_required()
def update_user():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_update_user,
        response=response,
        reference="User",
        add_to_session=False,
        action_type="update",
    )

    return response.build()


@user_bp.route("/update_team", methods=["PUT"])
@jwt_required()
def update_team():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_update_team,
        response=response,
        reference="Team",
        add_to_session=False,
        action_type="update",
    )

    return response.build()


@user_bp.route("/update_user_role", methods=["PUT"])
@jwt_required()
def update_user_role():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_update_user_role,
        response=response,
        reference="User Role",
        add_to_session=False,
        action_type="update",
    )

    return response.build()


@user_bp.route("/update_user_warehouse", methods=["PUT"])
@jwt_required()
def update_user_warehouse():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_update_user_warehouse,
        response=response,
        reference="User Warehouse",
        add_to_session=False,
        action_type="update",
    )

    return response.build()
