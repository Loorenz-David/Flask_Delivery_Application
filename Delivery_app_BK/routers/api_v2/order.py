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
from Delivery_app_BK.services.queries.order.list_orders import (
    list_orders as list_orders_service,
)
from Delivery_app_BK.services.queries.order.get_order import (
    get_order as get_order_service,
)
from Delivery_app_BK.services.queries.order_states.list_order_states import (
    list_order_states as list_order_states_service,
)
from Delivery_app_BK.services.commands.order.create_order import (
    create_order as create_order_service,
)
from Delivery_app_BK.services.commands.order.update_order import (
    update_order as update_order_service,
)
from Delivery_app_BK.services.commands.order.delete_order import (
    delete_order as delete_order_service,
)
from Delivery_app_BK.services.commands.order.update_order_delivery_plan import (
    update_order_delivery_plan as update_order_delivery_plan_service,
)
from Delivery_app_BK.services.commands.order_states.update_order_state import (
    update_order_state as update_order_state_service,
)
from Delivery_app_BK.services.queries.item.list_items import (
    list_items as list_items_service,
)


order_bp = Blueprint("api_v2_order_bp", __name__)


@order_bp.route("/", methods=["GET"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def list_orders():
    identity = get_jwt()
    ctx = ServiceContext(
        query_params=request.args,
        identity=identity,
    )
    
    outcome = run_service(lambda c: list_orders_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@order_bp.route("/states/", methods=["GET"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def list_order_states():
    identity = get_jwt()
    ctx = ServiceContext(
        query_params=request.args,
        identity=identity,
    )
    outcome = run_service(lambda c: list_order_states_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@order_bp.route("/", methods=["PUT"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def create_order():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
    )

    outcome = run_service(lambda c: create_order_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@order_bp.route("/", methods=["PATCH"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def update_order():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
    )
    outcome = run_service(lambda c: update_order_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        {},
        warnings=ctx.warnings,
    )


@order_bp.route("/", methods=["DELETE"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def delete_order():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    ctx = ServiceContext(
        incoming_data=incoming_data,
        identity=identity,
    )
    outcome = run_service(lambda c: delete_order_service(c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        {},
        warnings=ctx.warnings,
    )


@order_bp.route("/<int:order_id>", methods=["GET"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def get_order(order_id: int):
    identity = get_jwt()
    ctx = ServiceContext(
        query_params=request.args,
        identity=identity,
    )
    outcome = run_service(lambda c: get_order_service(order_id, c), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@order_bp.route("/<int:order_id>/items/", methods=["GET"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def list_order_items(order_id: int):
    identity = get_jwt()
    ctx = ServiceContext(
        query_params=request.args,
        identity=identity,
    )

    outcome = run_service(lambda c: list_items_service(c, order_id=order_id), ctx)
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        outcome.data,
        warnings=ctx.warnings,
    )


@order_bp.route("/<int:order_id>/state/<int:state_id>", methods=["PATCH"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def update_order_state(order_id: int, state_id: int):
    identity = get_jwt()
    ctx = ServiceContext(
        identity=identity,
    )
    outcome = run_service(
        lambda c: update_order_state_service(c, order_id, state_id),
        ctx,
    )
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        {},
        warnings=ctx.warnings,
    )


@order_bp.route("/<int:order_id>/plan/<int:plan_id>", methods=["PATCH"])
@jwt_required()
@role_required([ADMIN, ASSISTANT, DRIVER])
def update_order_delivery_plan(order_id: int, plan_id: int):
    identity = get_jwt()
    ctx = ServiceContext(
        identity=identity,
    )
    outcome = run_service(
        lambda c: update_order_delivery_plan_service(c, order_id, plan_id),
        ctx,
    )
    response = Response()

    if outcome.error:
        return response.build_unsuccessful_response(outcome.error)

    return response.build_successful_response(
        {},
        warnings=ctx.warnings,
    )
