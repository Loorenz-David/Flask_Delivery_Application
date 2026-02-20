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
from Delivery_app_BK.services.queries.item.list_items import list_items as list_items_service
from Delivery_app_BK.services.commands.item.create.create_item import (
    create_item as create_item_service,
)
from Delivery_app_BK.services.commands.item.update.update_item import (
    update_item as update_item_service,
)
from Delivery_app_BK.services.commands.item.update_item_state import (
    update_item_state as update_item_state_service,
)
from Delivery_app_BK.services.commands.item.update_item_position import (
    update_item_position as update_item_position_service,
)
from Delivery_app_BK.services.commands.item.delete.delete_item import (
    delete_item as delete_item_service,
)


item_bp = Blueprint("api_v2_item_bp", __name__)


@item_bp.route("/", methods=["GET"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def list_items():
    identity = get_jwt()
    ctx = ServiceContext(
        query_params=request.args,
        identity=identity,
    )
    outcome = run_service(lambda c: list_items_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@item_bp.route("/", methods=["POST"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def create_item():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True) or {}
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
    )
    outcome = run_service(lambda c: create_item_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@item_bp.route("/", methods=["PATCH"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def update_item():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True) or {}
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
    )
    outcome = run_service(lambda c: update_item_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        {},
        warnings=ctx.warnings,
    )


@item_bp.route("/", methods=["DELETE"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def delete_item():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True) or {}
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
    )
    print(incoming_data,'incoming')
    outcome = run_service(lambda c: delete_item_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        {},
        warnings=ctx.warnings,
    )


@item_bp.route("/<int:item_id>/state/<int:state_id>", methods=["PATCH"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def update_item_state(item_id: int, state_id: int):
    identity = get_jwt()
    ctx = ServiceContext(
        identity=identity,
    )
    outcome = run_service(
        lambda c: update_item_state_service(c, item_id, state_id),
        ctx,
    )
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        {},
        warnings=ctx.warnings,
    )


@item_bp.route("/<int:item_id>/position/<int:position_id>", methods=["PATCH"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def update_item_position(item_id: int, position_id: int):
    identity = get_jwt()
    ctx = ServiceContext(
        identity=identity,
    )
    outcome = run_service(
        lambda c: update_item_position_service(c, item_id, position_id),
        ctx,
    )
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        {},
        warnings=ctx.warnings,
    )
