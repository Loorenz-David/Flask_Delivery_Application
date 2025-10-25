from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from . import user_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models.tables.users_models import User, Team, UserRole, UserWarehouse
from Delivery_app_BK.models.managers.object_searcher import FindObjects


@user_bp.route("/query_user", methods=["POST"])
@jwt_required()
def query_user():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    FindObjects.find_objects(
        response=response,
        Model=User,
        identity=identity,
    )

    return response.build()


@user_bp.route("/query_team", methods=["POST"])
@jwt_required()
def query_team():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    FindObjects.find_objects(
        response=response,
        Model=Team,
        identity=identity,
    )

    return response.build()


@user_bp.route("/query_user_role", methods=["POST"])
@jwt_required()
def query_user_role():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    FindObjects.find_objects(
        response=response,
        Model=UserRole,
        identity=identity,
    )

    return response.build()


@user_bp.route("/query_user_warehouse", methods=["POST"])
@jwt_required()
def query_user_warehouse():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    FindObjects.find_objects(
        response=response,
        Model=UserWarehouse,
        identity=identity,
    )

    return response.build()
