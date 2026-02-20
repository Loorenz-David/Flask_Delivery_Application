from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt

from Delivery_app_BK.routers.utils.role_decorator import (
    role_required,
    ADMIN,
    ASSISTANT,
    DRIVER,
)
from Delivery_app_BK.routers.http.response import Response
from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.run_service import run_service
from Delivery_app_BK.services.queries.infrastructure.vehicle.list_vehicles import (
    list_vehicles as list_vehicles_service,
)
from Delivery_app_BK.services.queries.infrastructure.vehicle.get_vehicle import (
    get_vehicle as get_vehicle_service,
)
from Delivery_app_BK.services.commands.infrastructure.create.create_vehicle import (
    create_vehicle as create_vehicle_service,
)
from Delivery_app_BK.services.commands.infrastructure.update.update_vehicle import (
    update_vehicle as update_vehicle_service,
)
from Delivery_app_BK.services.commands.infrastructure.delete.delete_vehicle import (
    delete_vehicle as delete_vehicle_service,
)
from Delivery_app_BK.services.queries.infrastructure.warehouse.list_warehouses import (
    list_warehouses as list_warehouses_service,
)
from Delivery_app_BK.services.queries.infrastructure.warehouse.get_warehouse import (
    get_warehouse as get_warehouse_service,
)
from Delivery_app_BK.services.commands.infrastructure.create.create_warehouse import (
    create_warehouse as create_warehouse_service,
)
from Delivery_app_BK.services.commands.infrastructure.update.update_warehouse import (
    update_warehouse as update_warehouse_service,
)
from Delivery_app_BK.services.commands.infrastructure.delete.delete_warehouse import (
    delete_warehouse as delete_warehouse_service,
)


infrastructure_bp = Blueprint("api_v2_infrastructure_bp", __name__)


@infrastructure_bp.route("/vehicles/", methods=["GET"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def list_vehicles():
    identity = get_jwt()
    ctx = ServiceContext(
        query_params=request.args,
        identity=identity,
    )
    outcome = run_service(lambda c: list_vehicles_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@infrastructure_bp.route("/vehicles/", methods=["POST"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def create_vehicle():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True) or {}
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
    )
    outcome = run_service(lambda c: create_vehicle_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@infrastructure_bp.route("/vehicles/", methods=["PATCH"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def update_vehicle():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True) or {}
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
    )
    outcome = run_service(lambda c: update_vehicle_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        {},
        warnings=ctx.warnings,
    )


@infrastructure_bp.route("/vehicles/", methods=["DELETE"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def delete_vehicle():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True) or {}
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
    )
    outcome = run_service(lambda c: delete_vehicle_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        {},
        warnings=ctx.warnings,
    )


@infrastructure_bp.route("/vehicles/<int:vehicle_id>", methods=["GET"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def get_vehicle(vehicle_id: int):
    identity = get_jwt()
    ctx = ServiceContext(
        query_params=request.args,
        identity=identity,
    )
    outcome = run_service(lambda c: get_vehicle_service(vehicle_id, c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@infrastructure_bp.route("/warehouses/", methods=["GET"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def list_warehouses():
    identity = get_jwt()
    ctx = ServiceContext(
        query_params=request.args,
        identity=identity,
    )
    outcome = run_service(lambda c: list_warehouses_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@infrastructure_bp.route("/warehouses/", methods=["POST"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def create_warehouse():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True) or {}
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
    )
    outcome = run_service(lambda c: create_warehouse_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@infrastructure_bp.route("/warehouses/", methods=["PATCH"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def update_warehouse():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True) or {}
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
    )
    outcome = run_service(lambda c: update_warehouse_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        {},
        warnings=ctx.warnings,
    )


@infrastructure_bp.route("/warehouses/", methods=["DELETE"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def delete_warehouse():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True) or {}
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
    )
    outcome = run_service(lambda c: delete_warehouse_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        {},
        warnings=ctx.warnings,
    )


@infrastructure_bp.route("/warehouses/<int:warehouse_id>", methods=["GET"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def get_warehouse(warehouse_id: int):
    identity = get_jwt()
    ctx = ServiceContext(
        query_params=request.args,
        identity=identity,
    )
    outcome = run_service(lambda c: get_warehouse_service(warehouse_id, c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )
