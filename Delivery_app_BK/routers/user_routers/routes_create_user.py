from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from . import user_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.services import (
    service_create_user,
    service_create_team,
    service_create_user_role,
    service_create_user_warehouse,
)


@user_bp.route("/create_user", methods=["POST"])
@jwt_required()
def create_user():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_create_user,
        response=response,
        reference="User",
    )

    return response.build()


@user_bp.route("/create_team", methods=["POST"])
@jwt_required()
def create_team():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_create_team,
        response=response,
        reference="Team",
    )

    return response.build()


@user_bp.route("/create_user_role", methods=["POST"])
@jwt_required()
def create_user_role():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_create_user_role,
        response=response,
        reference="User Role",
    )

    return response.build()


@user_bp.route("/create_user_warehouse", methods=["POST"])
@jwt_required()
def create_user_warehouse():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_create_user_warehouse,
        response=response,
        reference="User Warehouse",
    )

    return response.build()
