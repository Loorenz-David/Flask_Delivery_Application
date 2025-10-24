from flask import request

from . import user_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models.tables.users_models import User, Team, UserRole, UserWarehouse
from Delivery_app_BK.models.managers.object_searcher import FindObjects


@user_bp.route("/query_user", methods=["POST"])
def query_user():
    response = Response()
    incoming_data = request.get_json()

    FindObjects.find_objects(
        response=response,
        Model=User,
        incoming_data=incoming_data,
    )

    return response.build()


@user_bp.route("/query_team", methods=["POST"])
def query_team():
    response = Response()
    incoming_data = request.get_json()

    FindObjects.find_objects(
        response=response,
        Model=Team,
        incoming_data=incoming_data,
    )

    return response.build()


@user_bp.route("/query_user_role", methods=["POST"])
def query_user_role():
    response = Response()
    incoming_data = request.get_json()

    FindObjects.find_objects(
        response=response,
        Model=UserRole,
        incoming_data=incoming_data,
    )

    return response.build()


@user_bp.route("/query_user_warehouse", methods=["POST"])
def query_user_warehouse():
    response = Response()
    incoming_data = request.get_json()

    FindObjects.find_objects(
        response=response,
        Model=UserWarehouse,
        incoming_data=incoming_data,
    )

    return response.build()
