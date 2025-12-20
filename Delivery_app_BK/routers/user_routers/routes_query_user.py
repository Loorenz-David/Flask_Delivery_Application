from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from Delivery_app_BK.routers.utils.role_decorator import role_required


from . import user_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models.tables.users_models import User, Team, UserRole, UserWarehouse, UserPrintLabelTemplates
from Delivery_app_BK.models.managers.object_searcher import FindObjects
from .users_default_data_request import (
    USER_REQUESTED_DATA,
    TEAM_REQUESTED_DATA,
    USER_ROLE_REQUESTED_DATA,
    USER_WAREHOUSE_REQUESTED_DATA,
    PRINT_TEMPLATE_REQUESTED_DATA,
)


@user_bp.route("/query_user", methods=["POST"])
@jwt_required()
@role_required([1, 2, 3])
def query_user():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)
    payload = response.incoming_data or {}
    if not isinstance(payload, dict):
        payload = {}
    if not payload.get('requested_data'):
        payload['requested_data'] = USER_REQUESTED_DATA
        response.incoming_data = payload

    FindObjects.find_objects(
        response=response,
        Model=User,
        identity=identity,
    )

    return response.build()


@user_bp.route("/query_team", methods=["POST"])
@jwt_required()
@role_required([1, 2, 3])
def query_team():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)
    payload = response.incoming_data or {}
    if not isinstance(payload, dict):
        payload = {}
    if not payload.get('requested_data'):
        payload['requested_data'] = TEAM_REQUESTED_DATA
        response.incoming_data = payload

    FindObjects.find_objects(
        response=response,
        Model=Team,
        identity=identity,
    )

    return response.build()


@user_bp.route("/query_user_role", methods=["POST"])
@jwt_required()
@role_required([1, 2, 3])
def query_user_role():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)
    payload = response.incoming_data or {}
    if not isinstance(payload, dict):
        payload = {}
    if not payload.get('requested_data'):
        payload['requested_data'] = USER_ROLE_REQUESTED_DATA
        response.incoming_data = payload

    FindObjects.find_objects(
        response=response,
        Model=UserRole,
        identity=identity,
    )

    return response.build()


@user_bp.route("/query_user_warehouse", methods=["POST"])
@jwt_required()
@role_required([1, 2])
def query_user_warehouse():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)
    payload = response.incoming_data or {}
    if not isinstance(payload, dict):
        payload = {}
    if not payload.get('requested_data'):
        payload['requested_data'] = USER_WAREHOUSE_REQUESTED_DATA
        response.incoming_data = payload

    FindObjects.find_objects(
        response=response,
        Model=UserWarehouse,
        identity=identity,
    )

    return response.build()


@user_bp.route("/query_templates_for_printing", methods=["POST"])
@jwt_required()
@role_required([1, 2, 3])
def query_templates_for_printing():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)
    payload = response.incoming_data or {}
    if not isinstance(payload, dict):
        payload = {}
    if not payload.get('requested_data'):
        payload['requested_data'] = PRINT_TEMPLATE_REQUESTED_DATA
    if 'query' not in payload:
        payload['query'] = {}
    response.incoming_data = payload

    FindObjects.find_objects(
        response=response,
        Model=UserPrintLabelTemplates,
        identity=identity,
    )

    return response.build()
