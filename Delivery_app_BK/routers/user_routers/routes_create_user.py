from flask import request

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
def create_user():
    response = Response()
    incoming_data = request.get_json()

    ObjectFiller.fill_object(
        data=incoming_data,
        fill_function=service_create_user,
        response=response,
        reference="User",
    )

    return response.build()


@user_bp.route("/create_team", methods=["POST"])
def create_team():
    response = Response()
    incoming_data = request.get_json()

    ObjectFiller.fill_object(
        data=incoming_data,
        fill_function=service_create_team,
        response=response,
        reference="Team",
    )

    return response.build()


@user_bp.route("/create_user_role", methods=["POST"])
def create_user_role():
    response = Response()
    incoming_data = request.get_json()

    ObjectFiller.fill_object(
        data=incoming_data,
        fill_function=service_create_user_role,
        response=response,
        reference="User Role",
    )

    return response.build()


@user_bp.route("/create_user_warehouse", methods=["POST"])
def create_user_warehouse():
    response = Response()
    incoming_data = request.get_json()

    ObjectFiller.fill_object(
        data=incoming_data,
        fill_function=service_create_user_warehouse,
        response=response,
        reference="User Warehouse",
    )

    return response.build()
